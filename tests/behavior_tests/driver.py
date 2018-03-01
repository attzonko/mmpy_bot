import time, re, six, threading, logging, sys, json
from six.moves import _thread
from websocket._exceptions import WebSocketConnectionClosedException, WebSocketTimeoutException
from mattermost_bot.bot import Bot, PluginsManager
from mattermost_bot.mattermost import MattermostClient
from mattermost_bot.dispatcher import MessageDispatcher
import driver_settings, bot_settings

logger = logging.getLogger(__name__)
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

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
		self.dm_chan = None	# direct message channel
		self.team_name = driver_settings.BOT_TEAM
		self.cm_name = driver_settings.BOT_CHANNEL
		self.cm_chan = None # common public channel
		self.gm_name = driver_settings.BOT_PRIVATE_CHANNEL
		self.gm_chan = None	# private channel
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
		"""Returns data if available, otherwise ''. Newlines indicate multiple messages """
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
					self.events.extend([json.loads(d) for d in json_data.split('\n')])
			time.sleep(1)

	def _retrieve_bot_user_ids(self):
		# get bot user info
		self.users_info = self.bot._client.api.post('/users/usernames', \
							[driver_settings.BOT_NAME, bot_settings.BOT_NAME])
		# get user ids
		for user in self.users_info:
			if user['username'] == self.bot_username:
				self.bot_userid = user['id']
			elif user['username'] == self.testbot_username:
				self.testbot_userid = user['id']

	def _create_dm_channel(self):
		"""create direct channel and get id"""
		response = self.bot._client.api.post('/channels/direct', \
						[self.bot_userid, self.testbot_userid])
		self.dm_chan = response['id']

	def _retrieve_cm_channel(self):
		"""create direct channel and get id"""
		response = self.bot._client.api.get('/teams/name/%s/channels/name/%s' % (self.team_name, self.cm_name))
		self.cm_chan = response['id']

	def _retrieve_gm_channel(self):
		"""create direct channel and get id"""
		response = self.bot._client.api.get('/teams/name/%s/channels/name/%s' % (self.team_name, self.gm_name))
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

	def validate_bot_direct_message(self, match):
		posts = self.bot._client.api.get('/channels/%s/posts' % self.dm_chan)
		last_response = posts['posts'][posts['order'][0]]
		if re.search(match, last_response['message']):
			return
		else:
			raise AssertionError('expected to get message like "{}", but got nothing'.format(match))

	def wait_for_bot_direct_message(self, match):
		self._wait_for_bot_message(self.dm_chan, match, tosender=False)

	def _wait_for_bot_message(self, channel, match, maxwait=10, tosender=True, thread=False):
		for _ in range(maxwait):
			time.sleep(1)
			if self._has_got_message_rtm(channel, match, tosender, thread=thread):
				break
		else:
			raise AssertionError('expected to get message like "{}", but got nothing'.format(match))

	def _has_got_message_rtm(self, channel, match, tosender=True, thread=False):
		if tosender is True:
			match = six.text_type(r'@{}: {}').format(self.bot_username, match)
		with self._events_lock:
			for event in self.events:
				if 'event' not in event or (event['event'] == 'posted' and 'data' not in event):
					print('Unusual event received: ' + repr(event))
				if event['event'] == 'posted':
					post_data = json.loads(event['data']['post'])
					if re.match(match, post_data['message'], re.DOTALL):
						return True
			return False

	def _send_channel_message(self, chan, msg, **kwargs):
		msg = self._format_message(msg, **kwargs)
		self._send_message_to_bot(chan, msg)

	def send_channel_message(self, msg, **kwargs):
		self._send_channel_message(self.cm_chan, msg, **kwargs)

	def validate_bot_channel_message(self, match):
		posts = self.bot._client.api.get('/channels/%s/posts' % self.cm_chan)
		last_response = posts['posts'][posts['order'][0]]
		if re.search(match, last_response['message']):
			return
		else:
			raise AssertionError('expected to get message like "{}", but got nothing'.format(match))

	def wait_for_bot_channel_message(self, match, tosender=True):
		self._wait_for_bot_message(self.cm_chan, match, tosender=tosender)

	def send_private_channel_message(self, msg, **kwargs):
		self._send_channel_message(self.gm_chan, msg, **kwargs)

	def wait_for_bot_private_channel_message(self, match, tosender=True):
		self._wait_for_bot_message(self.gm_chan, match, tosender=tosender)

	@classmethod
	def wait_for_bot_online(self):
		time.sleep(4)

	def clear_events(self):
		with self._events_lock:
			self.events = []
