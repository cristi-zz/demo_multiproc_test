import logging
import time
import pytest
import multiprocessing as mp

import misc
import controller


def hardware_surrogate():
    time.sleep(0.05)
    return 0

def action_object(x: int):
    print(f"Received state {x}")

def test_setup_and_start(proxy_manager):
    """
    Demonstrate the startup and shutdown of the controller. We must start it in another process so the test
    can shut it down through the stop_signal Event.

    """
    stop_signal = proxy_manager.Event()
    kwargs = {"hardware_sensor": hardware_surrogate, "timer_object": time.time,
              "callback_object":action_object, "stop_signal":stop_signal}
    main_proc = mp.Process(target=controller.sensor_reader_with_hysteresis, kwargs=kwargs)
    main_proc.start()
    time.sleep(1)
    stop_signal.set()
    main_proc.join(1)


def test_turn_zero_to_one(proxy_manager):
    """
    Demonstrates a complex setup: The hardware sensor generates values based on a timestamp, the calls to callback are recorded
    and everything is happening in another process.

    The Time_Accelerator shines here, because in 2 seconds we test ~ 100 seconds of activity.

    Note the setup (fairly complex) and how all the objects are depending on the same timestamp generator.

    """
    time_object = misc.Time_Accelerator(100)  # Timestamp generator

    # We set up the call listener so we can retrieve called functions, their parameters and time when they were called.
    misc.TestCustomManagerClass.register('action_recorder', lambda: misc.Remote_Call_Recorder(time_object),
                                         exposed=misc.Remote_Call_Recorder.get_fn_list_to_register())
    test_manager = misc.TestCustomManagerClass()
    test_manager.start()
    action_recorder = test_manager.action_recorder()

    # This is the hardware sensor. We mimic the delay.
    hardware_callable = misc.Time_Dependent_Iterator([(0, 0),(20, 1)], time_object)
    def delayed_hardware_callable():
        """
        This is needed because the hardware_sensor in controller is assumed to have some reading delay.
        """
        time.sleep(0.01)
        return hardware_callable()

    # The stop signal
    stop_signal = proxy_manager.Event()

    # We set up and start another process
    kwargs = {"hardware_sensor": delayed_hardware_callable, "timer_object": time_object,
              "callback_object":action_recorder, "stop_signal":stop_signal}
    main_proc = mp.Process(target=controller.sensor_reader_with_hysteresis, kwargs=kwargs)
    main_proc.start()

    time.sleep(1)  # 100 "seconds" should pass for the controller, by the means of Time_Accelerator

    # We stop the process by signaling it that it should stop and we wait for a clean exit. In actual tests one might
    # want to wait only few seconds (eg join(5) or sth).
    stop_signal.set()
    main_proc.join()

    # Let's assert what happened Were there any calls? At the "right" moment with the right values?
    calls = action_recorder.get_call_list()
    timestamps, args_list, kwargs_list = zip(*calls)
    assert len(calls) > 0, "There must be one transition"
    assert args_list[0][0] == 1, "The transition must be towards 1"
    assert timestamps[0] == pytest.approx(30, abs=3), "The transition should be around 20 + 10 seconds mark"


def test_turn_hysteresis_too_slow(proxy_manager):
    """
    We test the situation where the signal was not high enough time for the hysteresis to set.

    """
    time_object = misc.Time_Accelerator(100)

    misc.TestCustomManagerClass.register('action_recorder', lambda: misc.Remote_Call_Recorder(time_object),
                                         exposed=misc.Remote_Call_Recorder.get_fn_list_to_register())
    test_manager = misc.TestCustomManagerClass()
    test_manager.start()
    action_recorder = test_manager.action_recorder()

    hardware_callable = misc.Time_Dependent_Iterator([(0, 0), (5, 1), (8, 0)], time_object)

    def delayed_hardware_callable():
        """
        This is needed because the hardware_sensor in controller is assumed to have some reading delay.
        """
        time.sleep(0.01)
        return hardware_callable()

    stop_signal = proxy_manager.Event()
    kwargs = {"hardware_sensor": delayed_hardware_callable, "timer_object": time_object,
              "callback_object":action_recorder, "stop_signal":stop_signal}
    main_proc = mp.Process(target=controller.sensor_reader_with_hysteresis, kwargs=kwargs)
    main_proc.start()
    time.sleep(1)  # 100 "seconds" should pass for the controller, by the means of Time_Accelerator
    stop_signal.set()
    main_proc.join()

    # Let's assert what happened
    calls = action_recorder.get_call_list()
    assert len(calls) == 0, "There must be no transition. The time signal stayed at 1 is too short."
