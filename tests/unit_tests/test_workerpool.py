import time
import pytest
from mmpy_bot.utils import WorkerPool


def foo(msg):
    print(msg)
    time.sleep(10)


@pytest.fixture(scope="function")
def workerpool():
    return WorkerPool(foo, num_worker=10)


def test_get_busy_workers(workerpool):
    workerpool.add_task('hello')
    workerpool.add_task('hello again')
    workerpool.start()
    time.sleep(2)  # wait for worker threads to start
    if workerpool.get_busy_workers() != 2:
        raise AssertionError(workerpool.get_busy_workers())
