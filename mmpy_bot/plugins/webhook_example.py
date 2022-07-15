from mmpy_bot.driver import Driver
from mmpy_bot.function import listen_to, listen_webhook
from mmpy_bot.plugins.base import Plugin, PluginManager
from mmpy_bot.settings import Settings
from mmpy_bot.wrappers import ActionEvent, Message, WebHookEvent


class WebHookExample(Plugin):
    """Webhook plugin with examples of webhook server functionality."""

    def initialize(
        self, driver: Driver, plugin_manager: PluginManager, settings: Settings
    ):
        super().initialize(driver, plugin_manager, settings)
        self.webhook_host_url = settings.WEBHOOK_HOST_URL
        self.webhook_host_port = settings.WEBHOOK_HOST_PORT
        return self

    @listen_webhook("ping")
    @listen_webhook("pong")
    async def action_listener(self, event: WebHookEvent):
        """Listens to webhooks 'ping' and 'pong', and either updates the originating
        action post or sends a channel message to indicate that the webhook works."""
        if isinstance(event, ActionEvent):
            self.driver.respond_to_web(
                event,
                {
                    "update": {"message": event.context["text"], "props": {}},
                    "ephemeral_text": "You updated the post!",
                },
            )
        else:
            self.driver.create_post(
                event.body["channel_id"], f"Webhook {event.webhook_id} triggered!"
            )

    @listen_to("!button", direct_only=False)
    async def webhook_button(self, message: Message):
        """Creates a button that will trigger a webhook depending on the choice."""
        self.driver.reply_to(
            message,
            "",
            props={
                "attachments": [
                    {
                        "pretext": None,
                        "text": "Take your pick..",
                        "actions": [
                            {
                                "id": "sendPing",
                                "name": "Ping",
                                "integration": {
                                    "url": f"{self.webhook_host_url}:{self.webhook_host_port}/"
                                    "hooks/ping",
                                    "context": {
                                        "text": "The ping webhook works! :tada:",
                                    },
                                },
                            },
                            {
                                "id": "sendPong",
                                "name": "Pong",
                                "integration": {
                                    "url": f"{self.webhook_host_url}:{self.webhook_host_port}/"
                                    "hooks/pong",
                                    "context": {
                                        "text": "The pong webhook works! :tada:",
                                    },
                                },
                            },
                        ],
                    }
                ]
            },
        )
