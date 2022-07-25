import logging
import bisect
from typing import List, Tuple, Dict, Union
import multiprocessing as mp
import multiprocessing.managers
import time


class TestCustomManagerClass(mp.managers.SyncManager): pass
"""
Derived class for SyncManager. Used to create proxy objects for various tests.

"""

def assert_no_errors_in_logs(log_entries:List[logging.LogRecord]):
    """
    Will check if a list of logging records does not contain errors.

    Will raise an exception with corresponding error(s)

    :param log_entries:
    :return:
    """
    no_errors = True
    collected_errors = []
    for record in log_entries:
        if (record.levelno >= logging.ERROR):
            collected_errors.append(record.getMessage())
            no_errors = False
    assert no_errors, "\n".join(collected_errors)



class Time_Accelerator():
    """
    Creates a callable object that returns the current time multiplied by some constant. Useful to "accelerate" time in tests.

    """
    def __init__(self, acceleration_factor: float, offset_base_value: bool = True):
        """
        Sets the acceleration factor and if the time starts at 0.

        If offset_base_value is True, then the first value emitted is close to 0.
        If offset_base_value is False, the scaled value is added to the timestamp when the constructur was called.

        :param acceleration_factor:
        :param offset_base_value:
        """
        self.acceleration_factor = acceleration_factor
        self.offset_base_value = offset_base_value
        self.offset_value = time.time()
        if self.offset_base_value:
            self.zero_point = 0
        else:
            self.zero_point = time.time()

    def __call__(self) -> float:
        """
        Call the object to get some value out.

        Example:
            ta = Time_Accelerator(10)
            t1 = ta()
            ....
            t2 = ta()

        :return:
        """
        offsetted_value = time.time() - self.offset_value
        scaled_value = offsetted_value * self.acceleration_factor
        scaled_value += self.zero_point
        return scaled_value


class Time_Dependent_Iterator():
    """
    Objects of this class, when called, will issue a float (or a str) depending on the current timestamp.

    One can configure when and what values to be issued and this class will interpolate between values. One can also
    specify the timer object, in case a certain time accelerator is used. If set to None, it will be time.time
    """

    def __init__(self, value_list: List[Tuple[float, Union[float, str]]], time_obj: Time_Accelerator = None):
        """
        Sets up the object.

        value_list is a list of tuples, (timestamp, value). Example:
        [(0, 10),
         (10, 20),
         (15, 0),
         (20, 5),
         ]
         This means that calling our object will return 10 until second 9.9, then 20, until second 14.9, and then 0
         between second 15 and 19.9. After second 20, it will output 5, indefinitely.

         The 0.1 precision is just for show, in reality the < operation is used. The "seconds" is the timestamp obtained
         from time_obj. Using a Time_Accelerator is nice because it can "reset" the time to always start at second 0.

        """
        self.value_list = sorted(value_list, key=lambda x: x[0])
        self.key_list = [a[0] for a in value_list]
        if time_obj is None:
            time_obj = time.time
        self.time_obj = time_obj
        if len(value_list) > 0:
            self.lowest_ts = self.value_list[0][0]
            self.highest_ts = self.value_list[-1][0]
        else:
            assert "value_list must have at least one element"

    def __call__(self):
        crt_time = self.time_obj()
        if crt_time < self.lowest_ts:
            return self.value_list[0][1]
        if crt_time > self.highest_ts:
            return self.value_list[-1][1]
        i = bisect.bisect_left(self.key_list, crt_time)
        i = max(i, 1)
        value = self.value_list[i-1][1]
        return value


class Remote_Call_Recorder():
    """
    Objects of this class will record the calls made to them. Similar to what a mock does.

    This class is to be registered with TestCustomManagerClass and monkeypatched instead of actual function calls.
    The recorded messages can be retrieved with get_call_list()

    """
    def __init__(self, timer_object:Time_Accelerator = None):
        """
        Init the object. If there are no time "accelerators" in the code, one can pass None as timer_object.
        Otherwise, pass the Time_Accelerator object so the timestamps will make sense in the context of the trace.

        :param timer_object:
        """
        if timer_object is None:
            timer_object = time.time
        self.args_list = []
        self.kwargs_list = []
        self.call_timestamps = []
        self.timer_object = timer_object

    def __call__(self, *args, **kwargs):
        self.args_list.append(args)
        self.kwargs_list.append(kwargs)
        self.call_timestamps.append(self.timer_object())

    def get_call_list(self) -> List[Tuple[float, List, Dict]]:
        return list(zip(self.call_timestamps, self.args_list, self.kwargs_list))

    def clear_call_list(self):
        self.args_list.clear()
        self.kwargs_list.clear()
        self.call_timestamps.clear()

    @staticmethod
    def get_fn_list_to_register() -> List[str]:
        return ["__call__", "get_call_list", "clear_call_list"]
