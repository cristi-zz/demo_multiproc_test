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

