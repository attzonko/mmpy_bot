import time
import re
import six
import threading
import logging
import sys
import json
from six.moves import _thread
from websocket._exceptions import WebSocketConnectionClosedException, WebSocketTimeoutException  # noqa E501
from mmpy_bot.bot import Bot, PluginsManager
from mmpy_bot.mattermost import MattermostClient
from mmpy_bot.dispatcher import MessageDispatcher
from tests.behavior_tests.bots import driver_settings, responder_settings as bot_settings  # noqa E501


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class DriverBot(Bot):

    def __init__(self):
        self._client = MattermostClient(
            driver_settings.BOT_URL, driver_settings.BOT_TEAM,
            driver_settings.BOT_LOGIN, driver_settings.BOT_PASSWORD,
            driver_settings.SSL_VERIFY
        )
        self._plugins = PluginsManager()
        self._plugins.init_plugins()
        self._dispatcher = MessageDispatcher(self._client, self._plugins)


class Driver(object):

    def __init__(self):
        self.bot = DriverBot()
        self.bot_username = driver_settings.BOT_NAME
        self.bot_userid = None
        self.testbot_username = bot_settings.BOT_NAME
        self.testbot_userid = None
        self.dm_chan = None  # direct message channel
        self.team_name = driver_settings.BOT_TEAM
        self.cm_name = driver_settings.BOT_CHANNEL
        self.cm_chan = None  # common public channel
        self.gm_name = driver_settings.BOT_PRIVATE_CHANNEL
        self.gm_chan = None	 # private channel
        self.events = []
        self._events_lock = threading.Lock()

    def start(self):
        self._rtm_connect()
        self._retrieve_bot_user_ids()
        self._create_dm_channel()
        self._retrieve_cm_channel()
        self._retrieve_gm_channel()

    def _rtm_connect(self):
        self.bot._client.connect_websocket()
        self._websocket = self.bot._client.websocket
        self._websocket.sock.setblocking(0)
        _thread.start_new_thread(self._rtm_read_forever, tuple())

    def _websocket_safe_read(self):
        """Returns data if available, otherwise ''.
        Newlines indicate multiple messages """
        data = ''
        while True:
            # accumulated received data until no more events received
            # then exception triggered, then returns the accumulated data
            try:
                data += '{0}\n'.format(self._websocket.recv())
            except WebSocketConnectionClosedException:
                return data.rstrip()
            except WebSocketTimeoutException:
                return data.rstrip()
            except Exception:
                return data.rstrip()

    def _rtm_read_forever(self):
        while True:
            json_data = self._websocket_safe_read()
            if json_data != '':
                with self._events_lock:
                    self.events.extend(
                        [json.loads(d) for d in json_data.split('\n')])
            time.sleep(1)

    def _retrieve_bot_user_ids(self):
        # get bot user info
        self.users_info = self.bot._client.api.post(
            '/users/usernames',
            [driver_settings.BOT_NAME, bot_settings.BOT_NAME])
        # get user ids
        for user in self.users_info:
            if user['username'] == self.bot_username:
                self.bot_userid = user['id']
            elif user['username'] == self.testbot_username:
                self.testbot_userid = user['id']

    def _create_dm_channel(self):
        """create direct channel and get id"""
        response = self.bot._client.api.post(
            '/channels/direct', [self.bot_userid, self.testbot_userid])
        self.dm_chan = response['id']

    def _retrieve_cm_channel(self):
        """create direct channel and get id"""
        response = self.bot._client.api.get(
            '/teams/name/%s/channels/name/%s' %
            (self.team_name, self.cm_name))
        self.cm_chan = response['id']

    def _retrieve_gm_channel(self):
        """create direct channel and get id"""
        response = self.bot._client.api.get(
            '/teams/name/%s/channels/name/%s' %
            (self.team_name, self.gm_name))
        self.gm_chan = response['id']

    def _format_message(self, msg, tobot=True, colon=True, space=True):
        colon = ':' if colon else ''
        space = ' ' if space else ''
        if tobot:
            msg = u'@{}{}{}{}'.format(self.testbot_username, colon, space, msg)
        return msg

    def _send_message_to_bot(self, channel, msg):
        self.clear_events()
        self._start_ts = time.time()
        self.bot._client.channel_msg(channel, msg)

    def send_direct_message(self, msg, tobot=False, colon=True):
        msg = self._format_message(msg, tobot=tobot, colon=colon)
        self._send_message_to_bot(self.dm_chan, msg)

    def wait_for_bot_direct_message(self, match, maxwait=10):
        self._wait_for_bot_message(self.dm_chan, match, maxwait=maxwait,
                                   tosender=False)

    def _wait_for_bot_message(self, channel, match, maxwait=10,
                              tosender=True, thread=False):
        for _ in range(maxwait):
            time.sleep(1)
            if self._has_got_message_rtm(channel, match, tosender,
                                         thread=thread):
                return
        raise AssertionError(
            'expected to get message like "{}", but got nothing'
            .format(match))

    def _has_got_message_rtm(self, channel, match,
                             tosender=True, thread=False):
        if tosender is True:
            match = six.text_type(r'@{}: {}').format(self.bot_username, match)
        with self._events_lock:
            for event in self.events:
                if 'event' not in event or (
                        event['event'] == 'posted' and 'data' not in event):
                    print('Unusual event received: ' + repr(event))
                if event['event'] == 'posted':
                    post_data = json.loads(event['data']['post'])
                    if re.match(match, post_data['message'], re.DOTALL):
                        if thread:
                            if post_data['parent_id'] == "":
                                return False
                        return True
            return False

    def wait_for_bot_direct_file(self, maxwait=10):
        self._wait_for_bot_file(self.dm_chan, tosender=False, maxwait=maxwait)

    def _wait_for_bot_file(self, channel, maxwait=10,
                           tosender=True, thread=False):
        for _ in range(maxwait):
            time.sleep(1)
            if self._has_got_file_rtm(channel, tosender, thread=thread):
                return
        raise AssertionError('expected to get files, but got nothing')

    def _has_got_file_rtm(self, channel, tosender=True, thread=False):
        with self._events_lock:
            for event in self.events:
                if 'event' not in event or (
                        event['event'] == 'posted' and 'data' not in event):
                    print('Unusual event received: ' + repr(event))
                if event['event'] == 'posted':
                    post_data = json.loads(event['data']['post'])
                    if post_data.get('file_ids', []) is not []:
                        return True
            return False

    def _send_channel_message(self, chan, msg, **kwargs):
        msg = self._format_message(msg, **kwargs)
        self._send_message_to_bot(chan, msg)

    def send_channel_message(self, msg, **kwargs):
        self._send_channel_message(self.cm_chan, msg, **kwargs)

    def wait_for_bot_channel_message(self, match, tosender=True, thread=False):
        self._wait_for_bot_message(self.cm_chan, match,
                                   tosender=tosender, thread=thread)

    def send_private_channel_message(self, msg, **kwargs):
        self._send_channel_message(self.gm_chan, msg, **kwargs)

    def wait_for_bot_private_channel_message(self, match, tosender=True):
        self._wait_for_bot_message(self.gm_chan, match, tosender=tosender)

    def create_webhook(self):
        team = self.bot._client.api.get_team_by_name(
            team_name=driver_settings.BOT_TEAM)
        channel = self.bot._client.api.get_channel_by_name(
            team_id=team['id'],
            channel_name=driver_settings.BOT_CHANNEL)
        response = self.bot._client.api.hooks_create(channel_id=channel['id'],
                                                     username='pytest_name')
        if 'status_code' in response:
            raise AssertionError(
                'channel creation failed. error response: {}'
                .format(response))
        elif 'create_at' not in response.keys():
            raise AssertionError(
                'something wrong. webhook creation info is not returned: {}'
                .format(response))
        else:
            return response

    def get_webhook(self, webhook_id):
        response = self.bot._client.api.hooks_get(webhook_id=webhook_id)
        if 'status_code' in response:
            raise AssertionError(
                'hooks_get failed. error response: {}'
                .format(response))
        elif response['id'] != webhook_id:
            raise AssertionError(
                'something wrong with hooks_get. the result does not match.')
        else:
            return response

    def list_webhooks(self):
        response = self.bot._client.api.hooks_list()
        if isinstance(response, dict) and 'status_code' in response.keys():
            raise AssertionError(
                'list webhooks failed. error response: {}'
                .format(response))
        elif isinstance(response, list):
            return response
        else:
            raise AssertionError(
                'the returning response is not correct: {}'
                .format(response))

    def send_post_webhook(self, webhook_id):
        url = driver_settings.BOT_URL.split('/api')[0]
        response = self.bot._client.api.in_webhook(
            url='{}/hooks/{}'.format(url, webhook_id),
            channel=driver_settings.BOT_CHANNEL,
            text='hello',
            username='pytest_name')
        if response.status_code == 200:
            return response
        else:
            raise AssertionError(
                'send post through webhook failed. response: {}'
                .format(response))

    @classmethod
    def wait_for_bot_online(self):
        time.sleep(4)

    def clear_events(self):
        with self._events_lock:
            self.events = []
