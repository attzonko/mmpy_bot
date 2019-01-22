from tests.behavior_tests.fixture import driver  # noqa: F401


def test_allowed_users(driver):  # noqa: F811
    driver.send_channel_message('allowed_driver', tobot=True)
    driver.wait_for_bot_channel_message('Driver allowed!', tosender=True)
    driver.send_channel_message('not_allowed_driver', tobot=True)
    try:
        driver.wait_for_bot_channel_message('Driver not allowed!',
                                            tosender=True)
        raise AssertionError('response "Hello not allowed!" was not expected.')
    except AssertionError:
        pass


def test_allowed_users_by_email(driver):  # noqa: F811
    driver.send_channel_message('allowed_driver_by_email', tobot=True)
    driver.wait_for_bot_channel_message('Driver email allowed!', tosender=True)
