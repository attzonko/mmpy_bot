from functools import cached_property
from typing import Dict


class EventWrapper:
    """Wrapper around the body of a mattermost network event, e.g. new posts or webhook
    requests. Contains cached properties for convenient variable access.

    Arguments:
    - body: dictionary, body of the network request that contains this event.
    """

    def __init__(
        self,
        body: Dict,
    ):
        self.body = body


class Message(EventWrapper):
    @cached_property
    def id(self):
        return self.body["data"]["post"]["id"]

    @cached_property
    def user_id(self):
        return self.body["data"]["post"]["user_id"]

    @cached_property
    def text(self):
        return self.body["data"]["post"]["message"].strip()

    @cached_property
    def channel_id(self):
        return self.body["data"]["post"]["channel_id"]

    @cached_property
    def channel_name(self):
        return self.body["data"]["channel_name"]

    @cached_property
    def is_direct_message(self):
        return self.body["data"]["channel_type"] == "D"

    @cached_property
    def mentions(self):
        return self.body["data"].get("mentions", [])

    @cached_property
    def parent_id(self):
        return self.body["data"]["post"]["parent_id"]

    @cached_property
    def reply_id(self):
        return self.root_id or self.id

    @cached_property
    def root_id(self):
        return self.body["data"]["post"]["root_id"]

    @cached_property
    def sender_name(self):
        return self.body["data"].get("sender_name", "").strip().strip("@")

    @cached_property
    def team_id(self):
        return self.body["data"].get("team_id", "").strip()


class WebHookEvent(EventWrapper):
    """Wrapper around an incoming webhook post request.

    Arguments:
    - request_id: str, unique identifier of this web request
    - webhook_id: str, the webhook id that was triggered.
    """

    def __init__(
        self,
        *args,
        request_id: str,
        webhook_id: str,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.request_id = request_id
        self.webhook_id = webhook_id
        # Whether a web response was already sent to this request or not.
        self.responded = False

    @cached_property
    def text(self) -> str:
        return self.body.get("text")

    @cached_property
    def channel_name(self) -> str:
        return self.body.get("channel", self.body.get("channel_name"))

    @cached_property
    def props(self) -> Dict:
        return self.body.get("props", {})

    @cached_property
    def type(self) -> Dict:
        return self.body.get("type")


class ActionEvent(WebHookEvent):
    """Wrapper around an incoming webhook event that was triggered by an action, e.g.
    pressing a button or submitting a form."""

    @cached_property
    def channel_id(self):
        return self.body.get("channel_id")

    @cached_property
    def context(self):
        return self.body.get("context")

    @cached_property
    def data_source(self):
        return self.body.get("data_source")

    @cached_property
    def post_id(self):
        return self.body.get("post_id")

    @cached_property
    def team_id(self):
        return self.body.get("team_id")

    @cached_property
    def trigger_id(self):
        return self.body.get("trigger_id")

    @cached_property
    def user_id(self):
        return self.body.get("user_id")

    @cached_property
    def user_name(self):
        return self.body.get("user_name")
