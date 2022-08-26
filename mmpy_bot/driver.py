import queue
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

import mattermostautodriver
from aiohttp.client import ClientSession

from mmpy_bot.threadpool import ThreadPool
from mmpy_bot.webhook_server import WebHookServer
from mmpy_bot.wrappers import Message, WebHookEvent


class Driver(mattermostautodriver.Driver):
    user_id: str = ""
    username: str = ""

    def __init__(self, *args, num_threads=10, **kwargs):
        """Wrapper around the mattermostautodriver Driver with some convenience
        functions and attributes.

        Arguments:
        - num_threads: int, number of threads to use for the default worker threadpool.
        """
        super().__init__(*args, **kwargs)
        self.threadpool = ThreadPool(num_workers=num_threads)
        # Queue to communicate with the WebHookServer
        self.response_queue: Optional[queue.Queue] = None
        self.webhook_url = None

    def login(self, *args, **kwargs):
        super().login(*args, **kwargs)
        self.user_id = self.client._userid
        self.username = self.client._username

    def register_webhook_server(self, server: WebHookServer):
        self.response_queue = server.response_queue
        self.webhook_url = f"{server.url}:{server.port}/hooks"

    def create_post(
        self,
        channel_id: str,
        message: str,
        file_paths: Optional[Sequence[str]] = None,
        root_id: str = "",
        props: Dict = {},
        ephemeral_user_id: Optional[str] = None,
    ):
        """Create a post in the specified channel with the specified text.

        Supports sending ephemeral messages if bot permissions allow it. If any file
        paths are specified, those files will be uploaded to mattermost first and then
        attached.
        """
        if file_paths is None:
            file_paths = []

        file_ids = (
            self.upload_files(file_paths, channel_id) if len(file_paths) > 0 else []
        )

        post = dict(
            channel_id=channel_id,
            message=message,
            file_ids=file_ids,
            root_id=root_id,
            props=props,
        )

        if ephemeral_user_id:
            return self.posts.create_post_ephemeral(
                {
                    "user_id": ephemeral_user_id,
                    "post": post,
                }
            )

        return self.posts.create_post(post)

    def get_thread(self, post_id: str):
        warnings.warn(
            "get_thread is deprecated. Use get_post_thread instead", DeprecationWarning
        )
        return self.get_post_thread(post_id)

    def get_post_thread(self, post_id: str):
        """Wrapper around driver.posts.get_post_thread, which for some reason returns
        duplicate and wrongly ordered entries in the ordered list."""
        thread_info = self.posts.get_post_thread(post_id)

        id_stamps = []
        for id, post in thread_info["posts"].items():
            id_stamps.append((id, int(post["create_at"])))
        # Sort the posts by their timestamps
        sorted_stamps = sorted(id_stamps, key=lambda x: x[-1])
        # Overwrite the order with the sorted list
        thread_info["order"] = [id for id, stamp in sorted_stamps]
        return thread_info

    def get_user_info(self, user_id: str):
        """Returns a dictionary of user info."""
        return self.users.get_user(user_id)

    def react_to(self, message: Message, emoji_name: str):
        """Adds an emoji reaction to the given message."""
        return self.reactions.save_reaction(
            {
                "user_id": self.user_id,
                "post_id": message.id,
                "emoji_name": emoji_name,
            },
        )

    def reply_to(
        self,
        message: Message,
        response: str,
        file_paths: Optional[Sequence[str]] = None,
        props: Dict = {},
        ephemeral: bool = False,
        direct: bool = False,
    ):
        """Reply to the given message.

        Supports sending ephemeral messages if the bot permissions allow it. If the
        message is part of a thread, the reply will be added to that thread.

        Also supports replying privately by setting direct=True.
        """
        if file_paths is None:
            file_paths = []

        if direct and not message.is_direct_message:
            # NOTE we explicitly don't pass root_id as it would refer to a
            # post in a channel not a private session
            direct_args = dict(
                receiver_id=message.user_id,
                message=response,
                file_paths=file_paths,
                props=props,
                ephemeral_user_id=message.user_id if ephemeral else None,
            )

            return self.direct_message(**direct_args)

        reply_args = dict(
            channel_id=message.channel_id,
            message=response,
            root_id=message.reply_id,
            file_paths=file_paths,
            props=props,
            ephemeral_user_id=message.user_id if ephemeral else None,
        )

        return self.create_post(**reply_args)

    def direct_message(
        self,
        receiver_id: str,
        message: str,
        file_paths: Optional[Sequence[str]] = None,
        root_id: str = "",
        props: Dict = {},
        ephemeral_user_id: Optional[str] = None,
    ):
        # Private/direct messages are sent to a special channel that
        # includes the bot and the recipient
        direct_id = self.channels.create_direct_channel([self.user_id, receiver_id])[
            "id"
        ]

        return self.create_post(
            channel_id=direct_id,
            message=message,
            root_id=root_id,
            file_paths=file_paths,
            props=props,
            ephemeral_user_id=ephemeral_user_id,
        )

    def respond_to_web(self, event: WebHookEvent, response):
        """Send a web response to the given WebHookEvent."""
        self.response_queue.put((event.request_id, response))
        event.responded = True

    async def trigger_own_webhook(self, webhook_id: str, data: Dict):
        """Triggers a a webhook with id webhook_id on the running WebHookServer."""
        if not self.webhook_url:
            raise ValueError("The Driver is not aware of any running webhook server!")

        async with ClientSession() as session:
            return await session.post(
                f"{self.webhook_url}/{webhook_id}",
                json=data,
            )

    def upload_files(
        self, file_paths: Sequence[Union[str, Path]], channel_id: str
    ) -> List[str]:
        """Given a list of file paths and the channel id, uploads the corresponding
        files and returns a list their internal file IDs."""
        file_list = []
        for path in file_paths:
            path = Path(path)
            # Note: 'files' should be a name of an expected attribute in the body
            # but seems to be ignored when simply uploading files to mattermost
            file_list.append(
                (
                    "files",
                    (
                        path.name,
                        Path(path).read_bytes(),
                    ),
                )
            )

        result = self.files.upload_file(
            files=file_list, data={"channel_id": channel_id}
        )
        return list(info["id"] for info in result["file_infos"])
