import asyncio
import re
from datetime import datetime
from pathlib import Path

import click
import mattermostautodriver

from mmpy_bot.function import listen_to
from mmpy_bot.plugins.base import Plugin
from mmpy_bot.scheduler import schedule
from mmpy_bot.wrappers import Message


class ExamplePlugin(Plugin):
    """Default plugin with examples of bot functionality and usage."""

    @listen_to(
        "^admin$", direct_only=True, allowed_users=["admin", "root"], category="admin"
    )
    async def users_access(self, message: Message):
        """Showcases a function with restricted access."""
        self.driver.reply_to(message, "Access allowed!")

    @listen_to("^offtopic_channel$", allowed_channels=["off-topic"], category="admin")
    async def channels_access(self, message: Message):
        """Showcases a function which can only be used in specific channels."""
        self.driver.reply_to(message, "Access allowed!")

    @listen_to("^busy|jobs$", re.IGNORECASE, needs_mention=True, category="admin")
    async def busy_reply(self, message: Message):
        """Show the number of busy worker threads."""
        busy = self.driver.threadpool.get_busy_workers()
        self.driver.reply_to(
            message,
            f"Number of busy worker threads: {busy}",
        )

    @listen_to("hello_click", needs_mention=True, category="click")
    @click.command(help="An example click command with various arguments.")
    @click.argument("POSITIONAL_ARG", type=str)
    @click.option("--keyword-arg", type=float, default=5.0, help="A keyword arg.")
    @click.option("-f", "--flag", is_flag=True, help="Can be toggled.")
    def hello_click(
        self, message: Message, positional_arg: str, keyword_arg: float, flag: bool
    ):
        """A click function documented via docstring."""
        response = (
            "Received the following arguments:\n"
            f"- positional_arg: {positional_arg}\n"
            f"- keyword_arg: {keyword_arg}\n"
            f"- flag: {flag}\n"
        )
        self.driver.reply_to(message, response)

    @listen_to("^hello_channel$", needs_mention=True)
    async def hello_channel(self, message: Message):
        """Responds with a channel post rather than a reply."""
        self.driver.create_post(channel_id=message.channel_id, message="hello channel!")

    # Needs admin permissions
    @listen_to("^hello_ephemeral$", needs_mention=True)
    async def hello_ephemeral(self, message: Message):
        """Tries to reply with an ephemeral message, if the bot has system admin
        permissions."""
        try:
            self.driver.reply_to(message, "hello sender!", ephemeral=True)
        except mattermostautodriver.exceptions.NotEnoughPermissions:
            self.driver.reply_to(
                message, "I do not have permission to create ephemeral posts!"
            )

    @listen_to("^hello_react$", re.IGNORECASE, needs_mention=True)
    async def hello_react(self, message: Message):
        """Responds by giving a thumbs up reaction."""
        self.driver.react_to(message, "+1")

    @listen_to("^hello_file$", re.IGNORECASE, needs_mention=True)
    async def hello_file(self, message: Message):
        """Responds by uploading a text file."""
        file = Path("/tmp/hello.txt")
        file.write_text("Hello from this file!")
        self.driver.reply_to(message, "Here you go", file_paths=[file])

    @listen_to("^!hello_webhook$", re.IGNORECASE, category="webhook")
    async def hello_webhook(self, message: Message):
        """A webhook that says hello."""
        self.driver.client.call_webhook(
            "eauegoqk4ibxigfybqrsfmt48r",
            options={
                "username": "webhook_test",  # Requires the right webhook permissions
                "channel": "off-topic",
                "text": "Hello?",
                "attachments": [
                    {
                        "fallback": "Fallback text",
                        "title": "Title",
                        "author_name": "Author",
                        "text": "Attachment text here...",
                        "color": "#59afe1",
                    }
                ],
            },
        )

    @listen_to("^!info$")
    async def info(self, message: Message):
        """Responds with the user info of the requesting user."""
        user_email = self.driver.get_user_info(message.user_id)["email"]
        reply = (
            f"TEAM-ID: {message.team_id}\nUSERNAME: {message.sender_name}\n"
            f"EMAIL: {user_email}\nUSER-ID: {message.user_id}\n"
            f"IS-DIRECT: {message.is_direct_message}\nMENTIONS: {message.mentions}\n"
            f"MESSAGE: {message.text}"
        )
        self.driver.reply_to(message, reply)

    @listen_to("^ping$", re.IGNORECASE, needs_mention=True)
    async def ping_reply(self, message: Message):
        """Pong."""
        self.driver.reply_to(message, "pong")

    @listen_to(
        "^reply at (.*)$", re.IGNORECASE, needs_mention=True, category="schedule"
    )
    def schedule_once(self, message: Message, trigger_time: str):
        """Schedules a reply to be sent at the given time.

        Arguments:
        - triger_time (str): Timestamp of format %d-%m-%Y_%H:%M:%S,
            e.g. 20-02-2021_20:22:01. The reply will be sent at that time.
        """
        try:
            time = datetime.strptime(trigger_time, "%d-%m-%Y_%H:%M:%S")
            self.driver.reply_to(message, f"Scheduled message at {trigger_time}!")
            schedule.once(time).do(
                self.driver.reply_to, message, "This is the scheduled message!"
            )
        except ValueError as e:
            self.driver.reply_to(message, str(e))

    @listen_to(
        "^schedule every ([0-9]+)$",
        re.IGNORECASE,
        needs_mention=True,
        category="schedule",
    )
    def schedule_every(self, message: Message, seconds: int):
        """Schedules a reply every x seconds. Use the `cancel jobs` command to stop.

        Arguments:
        - seconds (int): number of seconds between each reply.
        """
        schedule.every(int(seconds)).seconds.do(
            self.driver.reply_to, message, f"Scheduled message every {seconds} seconds!"
        )

    @listen_to("^cancel jobs$", re.IGNORECASE, needs_mention=True, category="schedule")
    def cancel_jobs(self, message: Message):
        """Cancels all scheduled jobs, including recurring and one-time events."""
        schedule.clear()
        self.driver.reply_to(message, "Canceled all jobs.")

    @listen_to("^sleep ([0-9]+)$", needs_mention=True)
    async def sleep_reply(self, message: Message, seconds: str):
        """Sleeps for the specified number of seconds.
        Arguments:
            - seconds: How many seconds to sleep for."""
        self.driver.reply_to(message, f"Okay, I will be waiting {seconds} seconds.")
        await asyncio.sleep(int(seconds))
        self.driver.reply_to(message, "Done!")
