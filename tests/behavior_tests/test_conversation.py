from tests.behavior_tests.fixture import driver  # noqa: F401


def test_bot_respond_to_simple_message(driver):  # noqa: F811
    driver.send_direct_message('hello')
    driver.wait_for_bot_direct_message('hello sender!')


def test_bot_respond_to_simple_message_with_formatting(driver):  # noqa: F811
    driver.send_direct_message('hello_formatting')
    driver.wait_for_bot_direct_message('_hello_ sender!')


def test_bot_respond_to_simple_message_case_insensitive(driver):  # noqa: F811
    driver.send_direct_message('hEllO')
    driver.wait_for_bot_direct_message('hello sender!')


def test_bot_direct_message_with_at_prefix(driver):  # noqa: F811
    driver.send_direct_message('hello', tobot=True)
    driver.wait_for_bot_direct_message('hello sender!')
    driver.send_direct_message('hello', tobot=True, colon=False)
    driver.wait_for_bot_direct_message('hello sender!')


def test_bot_reply_to_channel_message(driver):  # noqa: F811
    driver.send_channel_message('hello')
    driver.wait_for_bot_channel_message('hello sender!')
    driver.send_channel_message('hello', colon=False)
    driver.wait_for_bot_channel_message('hello sender!')
    driver.send_channel_message('hello', space=False)
    driver.wait_for_bot_channel_message('hello sender!')
    driver.send_channel_message('hello', colon=False, space=False)
    driver.wait_for_bot_channel_message('hello channel!', tosender=False)


def test_bot_listen_to_channel_message(driver):  # noqa: F811
    driver.send_channel_message('hello', tobot=False)
    driver.wait_for_bot_channel_message('hello channel!', tosender=False)


def test_bot_reply_to_message_multiple_decorators(driver):  # noqa: F811
    driver.send_channel_message('hello_decorators')
    driver.wait_for_bot_channel_message('hello!', tosender=False)
    driver.send_channel_message('hello_decorators', tobot=False)
    driver.wait_for_bot_channel_message('hello!', tosender=False)
    driver.send_direct_message('hello_decorators')
    driver.wait_for_bot_direct_message('hello!')


def test_bot_reply_to_private_channel_message(driver):  # noqa: F811
    driver.send_private_channel_message('hello')
    driver.wait_for_bot_private_channel_message('hello sender!')
    driver.send_private_channel_message('hello', colon=False)
    driver.wait_for_bot_private_channel_message('hello sender!')


def test_bot_reply_to_message_thread(driver):  # noqa: F811
    driver.send_channel_message('hello_reply_threaded', tobot=False)
    driver.wait_for_bot_channel_message('hello threaded!', thread=True)
