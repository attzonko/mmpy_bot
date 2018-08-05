import subprocess
import pytest
from tests.behavior_tests.driver import Driver
from tests.behavior_tests import pytest_config


def _start_bot_process():
    """
    Function to run a bot for testing in subprocess
    """
    args = ['python', 'tests/behavior_tests/run_bot.py', ]
    return subprocess.Popen(args)


@pytest.fixture(scope='module')
def driver():
    driver = Driver()
    driver.start()
    p = _start_bot_process()
    driver.wait_for_bot_online()
    yield driver
    p.terminate()

#########################################################
# Actual test cases bellow
#########################################################


def test_bot_respond_to_simple_message(driver):
    driver.send_direct_message('hello')
    driver.wait_for_bot_direct_message('hello sender!')


def test_bot_respond_to_simple_message_with_formatting(driver):
    driver.send_direct_message('hello_formatting')
    driver.wait_for_bot_direct_message('_hello_ sender!')


def test_bot_respond_to_simple_message_case_insensitive(driver):
    driver.send_direct_message('hEllO')
    driver.wait_for_bot_direct_message('hello sender!')


def test_bot_direct_message_with_at_prefix(driver):
    driver.send_direct_message('hello', tobot=True)
    driver.wait_for_bot_direct_message('hello sender!')
    driver.send_direct_message('hello', tobot=True, colon=False)
    driver.wait_for_bot_direct_message('hello sender!')


# [ToDo] Implement this test together with the file upload function
@pytest.mark.skip(reason="no way of currently testing this")
def test_bot_upload_file(driver):
    pass


# [ToDo] Needs to find a better way in validating file upload by URL
@pytest.mark.skip(reason="no way of currently testing this")
def test_bot_upload_file_from_link(driver):
    # url = 'http://www.mattermost.org/wp-content/uploads/2016/03/logoHorizontal_WS.png'
    # fname = basename(url)
    # driver.send_direct_message('upload %s' % url)
    pass


def test_bot_reply_to_channel_message(driver):
    driver.send_channel_message('hello')
    driver.wait_for_bot_channel_message('hello sender!')
    driver.send_channel_message('hello', colon=False)
    driver.wait_for_bot_channel_message('hello sender!')
    driver.send_channel_message('hello', space=False)
    driver.wait_for_bot_channel_message('hello sender!')
    driver.send_channel_message('hello', colon=False, space=False)
    driver.wait_for_bot_channel_message('hello channel!', tosender=False)


def test_bot_listen_to_channel_message(driver):
    driver.send_channel_message('hello', tobot=False)
    driver.wait_for_bot_channel_message('hello channel!', tosender=False)


def test_bot_reply_to_message_multiple_decorators(driver):
    driver.send_channel_message('hello_decorators')
    driver.wait_for_bot_channel_message('hello!', tosender=False)
    driver.send_channel_message('hello_decorators', tobot=False)
    driver.wait_for_bot_channel_message('hello!', tosender=False)
    driver.send_direct_message('hello_decorators')
    driver.wait_for_bot_direct_message('hello!')


def test_bot_reply_to_private_channel_message(driver):
    driver.send_private_channel_message('hello')
    driver.wait_for_bot_private_channel_message('hello sender!')
    driver.send_private_channel_message('hello', colon=False)
    driver.wait_for_bot_private_channel_message('hello sender!')


@pytest.mark.skipif(pytest_config.DRIVER_ADMIN_PRIVILEGE is False,
                    reason="Needs admin privilege to create webhook.")
def test_bot_create_get_list_post_delete_webhook(driver):
    # test create webhook
    created = driver.create_webhook()
    # test get webhook
    driver.get_webhook(created['id'])
    # test list webhook
    hooklist = driver.list_webhooks()
    if created not in hooklist:
        raise AssertionError('something wrong, the hook {} should be found.'.format(created))
    # test send post through webhook
    driver.send_post_webhook(created['id'])


def test_allowed_users(driver):
    driver.send_channel_message('allowed_driver', tobot=True)
    driver.wait_for_bot_channel_message('Driver allowed!', tosender=True)
    driver.send_channel_message('not_allowed_driver', tobot=True)
    try:
        driver.wait_for_bot_channel_message('Driver not allowed!', tosender=True)
        raise AssertionError('response "Hello not allowed!" was not expected.')
    except AssertionError:
        pass