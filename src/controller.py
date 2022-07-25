from typing import Callable
import multiprocessing as mp
import time

def sensor_reader_with_hysteresis(hardware_sensor:Callable[[], float], timer_object:Callable[[], float],
                                  callback_object:Callable[[int], None], stop_signal:mp.Event()):
    """
    Read a sensor and trigger a callback when status is changed, with hysteresis.

    The hysteresis values are INTENTIONALLY hardcoded In practice, one might have a lot of modules with a lot of
    time constants that are too brittle to be changed. So it is better to leave them alone and "accelerate" time.
    Note: The heavy usage of dependency injection. Python can monkeypatch with ease, but this is cleaner, imho.
    Note: The code can't be tested in a single process, the test would block.
    """
    hy_lo = 0.4
    hy_hi = 0.8
    hy_time = 10
    crt_status = 0
    crt_time = None
    while not stop_signal.is_set():
        crt_signal = hardware_sensor() # We read the sensor. Assume some delay there
        record_activity = False
        if crt_status == 0 and crt_signal > hy_hi:
            record_activity = True
        if crt_status == 1 and crt_signal < hy_lo:
            record_activity = True
        if not record_activity:
            crt_time = None # A value not in the hysteresis activation band resets any clocks.
            continue
        if crt_time is None:
            # We init the hysterezis delay
            crt_time = timer_object()
        else:
            # We are still recording hysterezis delay ?
            if timer_object() - crt_time < hy_time:
                continue
            # We are beyond hold time, we switch state
            crt_status = 1 - crt_status
            # Notify the consumer
            callback_object(crt_status)
            crt_time = None
