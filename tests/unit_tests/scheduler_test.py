import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict
from unittest.mock import Mock

import pytest

from mmpy_bot import schedule
from mmpy_bot.threadpool import ThreadPool


def test_once():
    def job(path: str):
        print("job executed!")
        path = Path(path).write_text(str(time.time()))

    with tempfile.NamedTemporaryFile("r") as file:
        # Schedule the above to run once, two seconds from now
        start = time.time()
        schedule.once(datetime.fromtimestamp(start + 2)).do(job, file.name)
        assert file.readline() == ""

        # We trigger this every now and then, but the job should only execute at the
        # specified time.
        while time.time() < start + 3:
            schedule.run_pending()
            time.sleep(0.05)

        file.seek(0)
        # Verify that the written time was within 0.3 seconds of the expected time
        assert float(file.readline()) - 2 == pytest.approx(start, abs=0.3)


def test_once_single_call():
    mock = Mock()
    mock.side_effect = lambda: time.sleep(0.2)

    schedule.once().do(mock)

    assert repr(schedule.jobs[0]).startswith("Once at")

    for _ in range(10):
        schedule.run_pending()
        time.sleep(0.05)

    mock.assert_called_once()


def test_recurring_single_call():
    mock = Mock()
    mock.side_effect = lambda: time.sleep(0.2)

    schedule.every(2).seconds.do(mock)

    # Wait 2 seconds so we can run the task once
    time.sleep(2)

    # This loop corresponds to 0.1 seconds of total time and while there will
    # be 10 calls to run_pending() the mock function should only run once
    for _ in range(10):
        schedule.run_pending()
        time.sleep(0.01)

    mock.assert_called_once()


@pytest.mark.skip(reason="Test runs in Thread-1 (not MainThread) but still blocks")
def test_recurring_thread():
    def job(modifiable_arg: Dict):
        # Modify the variable, which should be shared with the main thread.
        modifiable_arg["count"] += 1

        # Since this should run in a separate thread, this shouldn't block anything.
        time.sleep(5)

    # Schedule the above to run every second in a separate thread, but not a separate
    # process.
    test_dict = {"count": 0}
    schedule.every(1).seconds.do(job, test_dict)

    start = time.time()
    end = start + 3.5  # We want to wait just over 3 seconds

    pool = ThreadPool(num_workers=10)

    pool.start_scheduler_thread(trigger_period=1)  # in seconds

    # Start the pool thread
    pool.start()

    while time.time() < end:
        # Wait until we reach our 3+ second deadline
        time.sleep(1)

    # Stop the pool and scheduler loop
    pool.stop()

    # Stop all scheduled jobs
    schedule.clear()
    # Nothing should happen from this point, even if we sleep another while
    time.sleep(2)

    # The job should have run a total of 3 times and the variable should be updated.
    assert test_dict == {"count": 3}


@pytest.mark.skip(reason="Test runs in Thread-1 (not MainThread) but still blocks")
def test_recurring_subprocess():
    def job(path: str, modifiable_arg: Dict):
        path = Path(path)
        # Increment number by one.
        current = path.read_text() or "0"
        new_number = int(current) + 1
        path.write_text(str(new_number))

        # Modify the variable, which should be local to this process only.
        modifiable_arg["changed"] = True

        # Since this should run in a separate process, this shouldn't block anything.
        time.sleep(5)

    with tempfile.NamedTemporaryFile("r") as file:
        # Schedule the above to run every second in a subprocess.
        test_dict = {}
        schedule.every(1).seconds.do(job, file.name, test_dict).tag("subprocess")

        # Assert nothing has changed yet
        file.readline() == "0"

        start = time.time()
        end = start + 3.5  # We want to wait just over 3 seconds
        pool = ThreadPool(num_workers=10)

        pool.start_scheduler_thread(trigger_period=1)  # in seconds

        # Start the pool thread
        pool.start()

        while time.time() < end:
            # Wait until we reach our 3+ second deadline
            time.sleep(1)

        # Stop the pool and scheduler loop
        pool.stop()

        # Stop all scheduled jobs
        schedule.clear()
        # Nothing should happen from this point, even if we sleep another while
        time.sleep(2)

        # We expect the job to have been launched 3 times, and since the sleep time
        # in the job should not be blocking, the number must have increased 3 times.
        file.seek(0)
        assert file.readline() == "3"
        assert test_dict == {}  # We expect the dict to not have been changed.
