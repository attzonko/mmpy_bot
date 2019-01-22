from datetime import datetime, timedelta
from tests.behavior_tests.fixture import driver  # noqa: F401

from mmpy_bot import settings


def test_bot_reply_specific_time(driver):  # noqa: F811
    t_time = datetime.now() + timedelta(seconds=2)
    str_t_time = t_time.strftime('%b-%d-%Y_%H:%M:%S')
    driver.send_direct_message(
        'reply "{0}" at {0}'.format(str_t_time), tobot=True)
    driver.wait_for_bot_direct_message(
        str_t_time, maxwait=settings.JOB_TRIGGER_PERIOD+10)


def test_bot_reply_every_seconds(driver):  # noqa: F811
    driver.send_direct_message('reply "alive" every 6 seconds', tobot=True)
    driver.wait_for_bot_direct_message(
        'alive', maxwait=settings.JOB_TRIGGER_PERIOD+10)
    driver.wait_for_bot_direct_message(
        'alive', maxwait=settings.JOB_TRIGGER_PERIOD+10)
    driver.send_direct_message('cancel jobs', tobot=True)
    driver.wait_for_bot_direct_message(
        'all jobs canceled.', maxwait=settings.JOB_TRIGGER_PERIOD+10)
