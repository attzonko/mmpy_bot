import json
import logging
import ssl
import time

import requests
import websocket
import websocket._exceptions

logger = logging.getLogger(__name__)


class MattermostAPI(object):
    def __init__(self, url, ssl_verify):
        self.url = url
        self.token = ""
        self.initial = None
        self.team_id = None
        self.ssl_verify = ssl_verify

    def _get_headers(self):
        return {"Authorization": "Bearer " + self.token}

    def get(self, request):
        return json.loads(
            requests.get(
                self.url + request,
                headers=self._get_headers(),
                verify=self.ssl_verify
            ).text)

    def post(self, request, data=None):
        return json.loads(requests.post(
            self.url + request,
            headers=self._get_headers(),
            data=json.dumps(data),
            verify=self.ssl_verify
        ).text)

    def login(self, name, email, password):
        props = {'name': name, 'login_id': email, 'password': password}
        p = requests.post(
            self.url + '/users/login', data=json.dumps(props),
            verify=self.ssl_verify
        )
        if p.status_code == 200:
            self.token = p.headers["Token"]
            self.load_initial_data()
            return json.loads(p.text)
        else:
            p.raise_for_status()

    def load_initial_data(self):
        self.initial = self.get('/users/initial_load')
        self.team_id = self.initial['teams'][0]['id']

    def create_post(self, user_id, channel_id, message, files=None, pid=""):
        create_at = int(time.time() * 1000)
        return self.post(
            '/teams/%s/channels/%s/posts/create' % (self.team_id, channel_id),
            {
                'user_id': user_id,
                'channel_id': channel_id,
                'message': message,
                'create_at': create_at,
                'filenames': files or [],
                'pending_post_id': user_id + ':' + str(create_at),
                'state': "loading",
                'parent_id': pid,
                'root_id': pid,
            })

    def update_post(self, message_id, user_id, channel_id, message, files=None, pid=""):
        return self.post(
            '/teams/%s/channels/%s/posts/update' % (self.team_id, channel_id),
            {
                'id': message_id,
                'channel_id': channel_id,
                'message': message,
            })

    def channel(self, channel_id):
        return self.get('/teams/%s/channels/%s/' % (self.team_id, channel_id))

    def get_channels(self):
        return self.get('/teams/%s/channels/' % self.team_id)

    def get_profiles(self, pagination_size=100):
        profiles = {}
        start = 0
        end = start + pagination_size

        current_page = self.get('/teams/%s/users/0/%s'
                                % (self.team_id, pagination_size))
        profiles.update(current_page)
        while len(current_page.keys()) == pagination_size:
            start = end
            end += pagination_size
            current_page = self.get('/teams/%s/users/%s/%s'
                                    % (self.team_id, start, end))
            profiles.update(current_page)
        return profiles

    def me(self):
        return self.get('/users/me')

    def user(self, user_id):
        return self.get_profiles()[user_id]

    def hooks_list(self):
        return self.get('/teams/%s/hooks/incoming/list' % self.team_id)

    def hooks_create(self, **kwargs):
        return self.post(
            '/teams/%s/hooks/incoming/create' % self.team_id, kwargs)

    @staticmethod
    def in_webhook(url, channel, text, username=None, as_user=None,
                   parse=None, link_names=None, attachments=None,
                   unfurl_links=None, unfurl_media=None, icon_url=None,
                   icon_emoji=None, ssl_verify=True):
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


class MattermostClient(object):
    def __init__(self, url, team, email, password, ssl_verify=True, login=1):
        self.users = {}
        self.channels = {}
        self.mentions = {}
        self.api = MattermostAPI(url, ssl_verify)
        self.user = None
        self.info = None
        self.websocket = None
        self.email = None
        self.team = team
        self.email = email
        self.password = password

        if login:
            self.login(team, email, password)

    def login(self, team, email, password):
        self.email = email
        self.user = self.api.login(team, email, password)
        self.info = self.api.me()
        return self.user

    def channel_msg(self, channel, message, pid=""):
        c_id = self.channels.get(channel, {}).get("id") or channel
        return self.api.create_post(self.user["id"], c_id, message, pid=pid)

    def update_msg(self, message_id, channel, message, pid=""):
        c_id = self.channels.get(channel, {}).get("id") or channel
        return self.api.update_post(message_id, self.user["id"],
                                    c_id, message, pid=pid)

    def get_users(self):
        return self.api.get_profiles()

    def connect_websocket(self):
        host = self.api.url.replace('http', 'ws').replace('https', 'wss')
        url = host + '/users/websocket'
        self._connect_websocket(url, cookie_name='MMAUTHTOKEN')
        return self.websocket.getstatus() == 101

    def _connect_websocket(self, url, cookie_name):
        self.websocket = websocket.create_connection(
            url, header=[
                "Cookie: %s=%s" % (cookie_name, self.api.token)
            ], sslopt={
                "cert_reqs": ssl.CERT_REQUIRED if self.api.ssl_verify \
                    else ssl.CERT_NONE
            })

    def messages(self, ignore_own_msg=False, filter_action=None):
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
                    if filter_action and post.get('event') != filter_action:
                        continue

                    if post.get('data', {}).get('post'):
                        dp = json.loads(post['data']['post'])
                        if ignore_own_msg is True and dp.get("user_id"):
                            if self.user["id"] == dp["user_id"]:
                                continue
                    yield post
                except ValueError:
                    pass

    def ping(self):
        self.websocket.ping()
