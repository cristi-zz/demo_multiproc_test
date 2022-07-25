import time
import pytest

from misc import Time_Accelerator, Time_Dependent_Iterator


def test_time_acc_call_offseted():
    ta = Time_Accelerator(1, True)
    t0_acc = ta()
    assert t0_acc == pytest.approx(0, abs=0.01)


def test_time_acc_call_no_offset():
    ta = Time_Accelerator(1, False)
    t0_acc = ta()
    t0_real = time.time()
    assert t0_acc == pytest.approx(t0_real, abs=0.01)


def test_time_acc_call_aceclerated():
    acc_factor = 10
    sleep_time = 1
    ta = Time_Accelerator(acc_factor, True)
    t0_acc = ta()
    time.sleep(sleep_time)
    t1_acc = ta()
    assert t1_acc - t0_acc == pytest.approx(acc_factor * sleep_time, abs=0.1)


def test_time_iterator_one_value():
    ta = Time_Accelerator(100)
    vals = [(5, 33.33)]
    td_val = Time_Dependent_Iterator(vals, ta)
    for k in range(100):
        v = td_val()
        assert v == pytest.approx(33.33)
        time.sleep(0.01)

def test_time_iterator_three_values():
    ta = Time_Accelerator(100)
    vals = [(5, 33.33), (50, 44.44), (99, 55.55)]
    collected_vals = set()
    td_val = Time_Dependent_Iterator(vals, ta)
    assert td_val() == pytest.approx(33.33)
    for k in range(120):
        v = td_val()
        collected_vals.add(v)
        time.sleep(0.01)
    assert td_val() == pytest.approx(55.55)
    assert len(collected_vals) == 3


def test_time_iterator_change_values_at_right_time():
    vals = [(0, 33.33), (50, 44.44)]
    ta = Time_Accelerator(100)
    td_val = Time_Dependent_Iterator(vals, ta)
    assert td_val() == pytest.approx(33.33)
    time.sleep(0.48)
    assert td_val() == pytest.approx(33.33)
    time.sleep(0.04)
    assert td_val() == pytest.approx(44.44)
