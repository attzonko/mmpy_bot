import pytest
from tests.behavior_tests.config import pytest_config
from tests.behavior_tests.fixture import driver  # noqa: F401


@pytest.mark.skipif(  # noqa: F811
        pytest_config.DRIVER_ADMIN_PRIVILEGE is False,
        reason="Needs admin privilege to create webhook.")
def test_bot_create_get_list_post_webhook(driver):
    # test create webhook
    created = driver.create_webhook()
    # test get webhook
    driver.get_webhook(created['id'])
    # test list webhook
    hooklist = driver.list_webhooks()
    if created not in hooklist:
        raise AssertionError(
            'something wrong, the hook {} should be found.'.format(created))
    # test send post through webhook
    driver.send_post_webhook(created['id'])
