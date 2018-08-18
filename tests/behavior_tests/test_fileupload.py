import pytest
from tests.behavior_tests.fixture import driver


def test_bot_upload_file(driver):
    driver.send_direct_message('show_me_src', tobot=True)
    driver.wait_for_bot_direct_file()


# [ToDo] Needs to find a better way in validating file upload by URL
@pytest.mark.skip(reason="no way of currently testing this")
def test_bot_upload_file_from_link(driver):
    # url = 'http://www.mattermost.org/wp-content/uploads/2016/03/logoHorizontal_WS.png'
    # fname = basename(url)
    # driver.send_direct_message('upload %s' % url)
    pass
