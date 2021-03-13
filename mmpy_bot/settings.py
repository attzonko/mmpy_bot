import collections
import os
from dataclasses import dataclass, field, fields
from typing import Sequence, get_args, get_origin  # type: ignore


def _get_comma_separated_list(string: str, type=str):
    values = string.split(",")
    # Convert to the specified type if necessary.
    if type is not str:
        values = list([type(value) for value in values])
    return values


@dataclass
class Settings:
    """Specifies the settings to be used by a chatbot. To run a chatbot, you should
    either create a custom Settings instance with the appropriate values, or modify them
    through environment variables.

    The order of priority in which settings are obtained is as follows:
    1. Environment variables
    2. Constructor arguments, if specified
    3. The default value set here.
    """

    MATTERMOST_URL: str = "https://chat.com"
    MATTERMOST_PORT: int = 443
    BOT_TOKEN: str = "token"
    BOT_TEAM: str = "team_name"
    SSL_VERIFY: bool = True
    WEBHOOK_HOST_ENABLED: bool = False
    WEBHOOK_HOST_URL: str = "http://127.0.0.1"
    WEBHOOK_HOST_PORT: int = 8579
    DEBUG: bool = False
    IGNORE_USERS: Sequence[str] = field(default_factory=list)
    # How often to check whether any scheduled jobs need to be run, default every second
    SCHEDULER_PERIOD: float = 1.0

    SCHEME: str = field(init=False)  # Will be taken from the URL. Defaults to https.

    def __post_init__(self):
        # Check if any fields need to be overridden by environment variables
        self._check_environment_variables()

        if "://" in self.MATTERMOST_URL:
            self.SCHEME, self.MATTERMOST_URL = self.MATTERMOST_URL.split("://")
        else:
            self.SCHEME = "https"

    def _check_environment_variables(self):
        for f in fields(self):
            if f.name in os.environ:
                self._set_field(f, os.environ[f.name])

    def _set_field(self, f, value: str):
        if f.default_factory is list:
            # Assert that the type spec of this attribute is indeed a sequence
            if not issubclass(get_origin(f.type), collections.abc.Sequence):
                raise TypeError(
                    f"Since attribute {f.name} has `default_factory=list`, it "
                    "should be specified as a Sequence (or a subclass of it). "
                    f"The actual type is {f.type}."
                )
            if len(get_args(f.type)) == 0:
                raise TypeError(
                    f"Attribute {f.name} was specified as a Sequence without "
                    "specifying what kind of objects it contains."
                )
            # Use get_args to find out what kind of sequence it is.
            value = _get_comma_separated_list(value, type=get_args(f.type)[0])
        elif f.type in [int, float, str, bool]:  # type: ignore
            value = f.type(value)
        else:
            raise TypeError(
                f"Attribute {f.name} has type {f.type}, which is not supported."
                "Consider updating Settings.__post_init__ to support converting"
                " environment variables to this type."
            )
        setattr(self, f.name, value)
