import os

from mmpy_bot import Settings


def test_constructor():
    default = Settings()
    assert default.MATTERMOST_URL == "chat.com"
    assert default.SCHEME == "https"
    assert default.IGNORE_USERS == []

    manual = Settings(
        MATTERMOST_URL="http://website.com", IGNORE_USERS=["me", "someone_else"]
    )
    assert manual.MATTERMOST_URL == "website.com"
    assert manual.SCHEME == "http"
    assert manual.IGNORE_USERS == ["me", "someone_else"]

    # Test default scheme
    assert Settings(MATTERMOST_URL="website.com").SCHEME == "https"


def test_environment():
    assert Settings(MATTERMOST_URL="website.com").MATTERMOST_URL == "website.com"

    os.environ["MATTERMOST_URL"] = "test_site.org"
    os.environ["IGNORE_USERS"] = "me,someone_else"
    s = Settings(MATTERMOST_URL="website.com")
    assert s.MATTERMOST_URL == "test_site.org"
    # The environment variable should be parsed into a list.
    assert s.IGNORE_USERS == ["me", "someone_else"]
