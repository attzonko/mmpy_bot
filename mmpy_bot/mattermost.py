import json
import logging
import ssl
import requests
import socket
import websocket
import websocket._exceptions

logger = logging.getLogger(__name__)


class MattermostAPI(object):
    def __init__(self, url, ssl_verify, token):
        self.url = url
        self.token = token
        self.initial = None
        self.default_team_id = None  # the first team in API returned value
        self.teams_channels_ids = None  # struct:{team_id:[channel_id,...],...}
        self.ssl_verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings(
                requests.packages.urllib3.exceptions.InsecureRequestWarning)

    def _get_headers(self):
        return {"Authorization": "Bearer " + self.token}

    def channel(self, channel_id):
        channel = {'channel': self.get('/channels/{}'.format(channel_id))}
        return channel

    def create_reaction(self, user_id, post_id, emoji_name):
        return self.post(
            '/reactions',
            {
                'user_id': user_id,
                'post_id': post_id,
                'emoji_name': emoji_name,
            })

    def delete_reaction(self, user_id, post_id, emoji_name):
        return self.delete(
            '/users/{0}/posts/{1}/reactions/{2}'.format(
                user_id, post_id, emoji_name))

    def create_post(self, user_id, channel_id, message,
                    files=None, pid="", props=None):
        return self.post(
            '/posts',
            {
                'channel_id': channel_id,
                'message': message,
                'file_ids': files or [],
                'root_id': pid,
                'props': props or {}
            })

    @staticmethod
    def create_user_dict(self, v4_dict):
        new_dict = {}
        new_dict[v4_dict['id']] = v4_dict
        return new_dict

    def get(self, request):
        return json.loads(
            requests.get(
                self.url + request,
                headers=self._get_headers(),
                verify=self.ssl_verify
            ).text)

    def get_channel_by_name(self, channel_name, team_id=None):
        return self.get('/teams/{}/channels/name/{}'.format(
            team_id, channel_name))

    def get_channels(self, team_id=None):
        if team_id is None:
            team_id = self.default_team_id
        return self.get('/users/me/teams/{}/channels'.format(team_id))

    def get_file_link(self, file_id):
        return self.get('/files/{}/link'.format(file_id))

    def get_team_by_name(self, team_name):
            return self.get('/teams/name/{}'.format(team_name))

    def get_team_id(self, channel_id):
        for team_id, channels in self.teams_channels_ids.items():
            if channel_id in channels:
                return team_id
        return None

    def get_user_info(self, user_id):
        return self.get('/users/{}'.format(user_id))

    def hooks_create(self, **kwargs):
        return self.post(
            '/hooks/incoming', kwargs)

    def hooks_get(self, webhook_id):
        return self.get(
            '/hooks/incoming/{}'.format(webhook_id))

    def hooks_list(self):
        return self.get('/hooks/incoming')

    @staticmethod
    def in_webhook(url, channel, text, username=None, as_user=None,
                   parse=None, link_names=None, attachments=None,
                   unfurl_links=None, unfurl_media=None, icon_url=None,
                   icon_emoji=None, ssl_verify=True, **kwargs):
        return requests.post(
            url, data={
                'payload': json.dumps({
                    'channel': channel,
                    'text': text,
                    'username': username,
                    'as_user': as_user,
                    'parse': parse,
                    'link_names': link_names,
                    'attachments': attachments,
                    'unfurl_links': unfurl_links,
                    'unfurl_media': unfurl_media,
                    'icon_url': icon_url,
                    'icon_emoji': icon_emoji})
            }, verify=ssl_verify)

    def login(self, team, account, password):
            props = {'login_id': account, 'password': password}
            response = self._login(props)
            if response.status_code in [301, 302, 307]:
                # reset self.url to the new URL
                self.url = response.headers['Location'].replace(
                        '/users/login', '')
                # re-try login if redirected
                response = self._login(props)
            if response.status_code == 200:
                self.token = response.headers["Token"]
                self.load_initial_data()
                user = json.loads(response.text)
                return user
            else:
                response.raise_for_status()

    def _login(self, props):
        return requests.post(
            self.url + '/users/login',
            data=json.dumps(props),
            verify=self.ssl_verify,
            allow_redirects=False)

    def load_initial_data(self):
        self.teams = self.get('/users/me/teams')
        if len(self.teams) == 0:
            raise AssertionError(
                    'User account of this bot does not join any team yet.')
        self.default_team_id = self.teams[0]['id']
        self.teams_channels_ids = {}
        for team in self.teams:
            self.teams_channels_ids[team['id']] = []
            # get all channels belonging to each team
            for channel in self.get_channels(team['id']):
                self.teams_channels_ids[team['id']].append(channel['id'])

    def me(self):
        return self.get('/users/me')

    def post(self, request, data):
        return json.loads(requests.post(
            self.url + request,
            headers=self._get_headers(),
            data=json.dumps(data),
            verify=self.ssl_verify
        ).text)

    def delete(self, request):
        return json.loads(requests.delete(
            self.url + request,
            headers=self._get_headers(),
            verify=self.ssl_verify
        ).text)

    def put(self, request, data):
        return json.loads(requests.put(
            self.url + request,
            headers=self._get_headers(),
            data=json.dumps(data),
            verify=self.ssl_verify
        ).text)

    def update_post(self, message_id, user_id, channel_id,
                    message, files=None, pid=""):
        return self.put(
            '/posts/%s/patch' % message_id,
            {
                'message': message,
            })

    def user(self, user_id):
        return self.get_user_info(user_id)

    def upload_file(self, file, channel_id):
        files = {
            'files': file,
            'channel_id': (None, channel_id)
        }
        return json.loads(requests.post(
            self.url + '/files',
            headers=self._get_headers(),
            files=files,
            verify=self.ssl_verify
        ).text)


class MattermostClient(object):
    def __init__(self, url, team, email, password, ssl_verify=True,
                 token=None, ws_origin=None):
        self.users = {}
        self.channels = {}
        self.mentions = {}
        self.api = MattermostAPI(url, ssl_verify, token)
        self.user = None
        self.websocket = None
        self.email = None
        self.team = team
        self.email = email
        self.password = password
        self.ws_origin = ws_origin

        if token:
            self.user = self.api.me()
        else:
            self.login(team, email, password)

    def login(self, team, email, password):
        self.email = email
        self.user = self.api.login(team, email, password)
        return self.user

    def react_msg(self, post_id, emoji_name):
        return self.api.create_reaction(self.user["id"],
                                        post_id, emoji_name)

    def remove_reaction(self, post_id, emoji_name):
        return self.api.delete_reaction(self.user["id"],
                                        post_id, emoji_name)

    def channel_msg(self, channel, message, files=None, pid="", props=None):
        c_id = self.channels.get(channel, {}).get("id") or channel
        return self.api.create_post(self.user["id"], c_id,
                                    "{}".format(message), files, pid,
                                    props=props or {})

    def update_msg(self, message_id, channel, message, pid=""):
        c_id = self.channels.get(channel, {}).get("id") or channel
        return self.api.update_post(message_id, self.user["id"],
                                    c_id, message, pid=pid)

    def connect_websocket(self):
        host = self.api.url.replace('http', 'ws').replace('https', 'wss')
        url = host + '/websocket'
        self._connect_websocket(url, cookie_name='MMAUTHTOKEN')
        return self.websocket.getstatus() == 101

    def _connect_websocket(self, url, cookie_name):
        self.websocket = websocket.create_connection(
            url, header=["Cookie: %s=%s" % (cookie_name, self.api.token)],
            origin=self.ws_origin,
            sslopt={
                "cert_reqs": ssl.CERT_REQUIRED if self.api.ssl_verify
                else ssl.CERT_NONE})

    def messages(self, ignore_own_msg=False, filter_actions=None):
        filter_actions = filter_actions or []
        if not self.connect_websocket():
            return
        while True:
            try:
                data = self.websocket.recv()
            except websocket._exceptions.WebSocketException:
                if not self.connect_websocket():
                    raise
                continue
            if data:
                try:
                    post = json.loads(data)
                    event_action = post.get('event')
                    if event_action not in filter_actions:
                        continue

                    if event_action == 'posted':
                        if post.get('data', {}).get('post'):
                            dp = json.loads(post['data']['post'])
                            if ignore_own_msg is True and dp.get("user_id"):
                                if self.user["id"] == dp["user_id"]:
                                    continue
                        yield post
                    elif event_action in ['added_to_team', 'leave_team',
                                          'user_added', 'user_removed']:
                        self.api.load_initial_data()  # reload teams & channels
                except ValueError:
                    pass

    def ping(self):
        try:
            self.websocket.ping()
        except socket.error:
            logger.error('\n'.join([
                'socket.error while pinging the mattermost server',
                'possible causes: expired cookie or broken socket pipe'
            ]))
            if not self.connect_websocket():  # try to re-connect
                logger.info('reconnecting websocket ... failed')
            else:
                logger.info('reconnecting websocket ... succeeded')
