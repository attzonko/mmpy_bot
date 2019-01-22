import pytest
from mmpy_bot import settings
from mmpy_bot.bot import Bot


def test_API_version_check():
    settings.MATTERMOST_API_VERSION = 3
    with pytest.raises(ValueError):
        bot = Bot()  # noqa: F841; pylint: disable=unused-variable
