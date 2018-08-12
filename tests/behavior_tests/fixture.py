import subprocess
import pytest
from tests.behavior_tests.bots.driver import Driver


def _start_bot_process():
    """
    Function to run a bot for testing in subprocess
    """
    args = ['python', 'tests/behavior_tests/bots/responder.py', ]
    return subprocess.Popen(args)


@pytest.fixture(scope='module')
def driver():
    driver = Driver()
    driver.start()
    p = _start_bot_process()
    driver.wait_for_bot_online()
    yield driver
    p.terminate()
