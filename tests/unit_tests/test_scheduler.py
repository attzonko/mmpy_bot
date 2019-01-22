import pytest
import time
from datetime import datetime, timedelta
from mmpy_bot.scheduler import schedule


def foo(msg):
    print(msg)


def foo2(dict_acc):
    dict_acc['acc'] += 1


@pytest.fixture(scope="function")
def my_schedule():
    return schedule


def test_add_onetime_job_without_trigger_time(my_schedule):
    my_schedule.once().do(foo, msg='hello')
    if len(my_schedule.jobs) != 1:
        raise AssertionError("Job is not added to schedule.")
    time.sleep(1)  # wait for worker threads to start
    my_schedule.run_pending()
    if len(my_schedule.jobs) != 0:
        raise AssertionError("Job is not executed by schedule.")


def test_add_onetime_job_with_trigger_time(my_schedule):
    run_time = datetime.now() + timedelta(seconds=2)
    my_schedule.once(run_time).do(foo, msg='hello')
    if len(my_schedule.jobs) != 1:
        raise AssertionError("Job is not added to schedule.")
    time.sleep(3)  # wait for worker threads to start
    my_schedule.run_pending()
    if len(my_schedule.jobs) != 0:
        raise AssertionError("Job is not executed by schedule.")


def test_add_periodic_job(my_schedule):
    dict_acc = {'acc': 0}
    my_schedule.every(1).seconds.do(foo2, dict_acc=dict_acc)
    time.sleep(2)  # wait for worker threads to start
    my_schedule.run_pending()
    time.sleep(2)  # wait for worker threads to start
    my_schedule.run_pending()
    if dict_acc['acc'] != 2:
        raise AssertionError("Incorrect periodic job execution.")
