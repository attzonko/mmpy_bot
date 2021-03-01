from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class Settings:
    """Simple dataclass to hold some values.

    Will probably be removed in the future. To run a chatbot, you should always create a
    custom Settings instance with the appropriate values.
    """

    MATTERMOST_URL: str = "https://chat.com"
    MATTERMOST_PORT: int = 443
    BOT_TOKEN: str = "token"
    BOT_TEAM: str = "team_name"
    SSL_VERIFY: bool = True
    WEBHOOK_HOST_ENABLED: bool = True
    WEBHOOK_HOST_URL: str = "http://127.0.0.1"
    WEBHOOK_HOST_PORT: int = 8579
    DEBUG: bool = False
    IGNORE_USERS: Sequence[str] = field(default_factory=list)
    # How often to check whether any scheduled jobs need to be run, default every second
    SCHEDULER_PERIOD: float = 1.0

    SCHEME: str = field(init=False)  # Will be taken from the URL. Defaults to https.

    def __post_init__(self):
        if "://" in self.MATTERMOST_URL:
            self.SCHEME, self.MATTERMOST_URL = self.MATTERMOST_URL.split("://")
        else:
            self.SCHEME = "https"
