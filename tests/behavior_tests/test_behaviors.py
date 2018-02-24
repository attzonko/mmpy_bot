import subprocess, time
import pytest
from driver import Driver

def _start_bot_process():
    """
    Function to run a bot for testing in subprocess
    """
    args = ['python', 'tests/behavior_tests/run_bot.py',]
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
def test_bot_upload_file(driver):
    pass

# [ToDo] Needs to find a better way in validating file upload by URL
def test_bot_upload_file_from_link(driver):
    #url = 'http://www.mattermost.org/wp-content/uploads/2016/03/logoHorizontal_WS.png'
    #fname = basename(url)
    #driver.send_direct_message('upload %s' % url)
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