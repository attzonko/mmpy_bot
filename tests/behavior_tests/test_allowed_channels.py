from tests.behavior_tests.fixture import driver  # noqa: F401


def test_allowed_channels(driver):  # noqa: F811

    driver.send_direct_message('allowed_channel', tobot=True)
    driver.wait_for_bot_direct_message(
        'Driver in channel allowed!')

    driver.send_private_channel_message('allowed_channel', tobot=True)
    driver.wait_for_bot_private_channel_message(
        'Driver in channel allowed!', tosender=True)

    driver.send_private_channel_message('not_allowed_channel', tobot=True)
    try:
        driver.wait_for_bot_private_channel_message(
            'Driver in channel NOT allowed!', tosender=True)
        raise AssertionError(
            'response "Driver in channel NOT allowed" was not expected.')
    except AssertionError:
        pass
