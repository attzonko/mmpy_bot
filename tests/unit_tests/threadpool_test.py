import time

import pytest

from mmpy_bot.driver import ThreadPool


@pytest.fixture(scope="function")
def threadpool():
    pool = ThreadPool(num_workers=10)
    yield pool
    pool.stop()  # if the pool was started, stop it.


class TestThreadPool:
    def foo(self, msg: str):
        print(msg)
        time.sleep(5)

    def test_get_busy_workers(self, threadpool):
        assert not threadpool.alive
        threadpool.start()
        assert threadpool.alive
        assert threadpool.get_busy_workers() == 0
        threadpool.add_task(self.foo, ["hello"])
        threadpool.add_task(self.foo, ["hello again"])
        time.sleep(1)  # wait for workers to start
        print(threadpool.get_busy_workers())
        assert threadpool.get_busy_workers() == 2
        time.sleep(6)  # wait for workers to finish
        assert threadpool.get_busy_workers() == 0
        threadpool.stop()
        assert not threadpool.alive
