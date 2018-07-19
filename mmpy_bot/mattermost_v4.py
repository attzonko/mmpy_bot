import json
import logging

import requests

from mmpy_bot.mattermost import MattermostClient, MattermostAPI

logger = logging.getLogger(__name__)


class MattermostAPIv4(MattermostAPI):

    def login(self, team, account, password):
        props = {'login_id': account, 'password': password}
        response = requests.post(
            self.url + '/users/login',
            data=json.dumps(props),
            verify=self.ssl_verify,
            allow_redirects=False)
        if response.status_code in [301, 302, 307]:
            # reset self.url to the new URL
            self.url = response.headers['Location'].replace('/users/login', '')
            # re-try login if redirected
            response = requests.post(
                self.url + '/users/login',
                data=json.dumps(props),
                verify=self.ssl_verify,
                allow_redirects=False)
        if response.status_code == 200:
            self.token = response.headers["Token"]
            self.load_initial_data()
            self.user = json.loads(response.text)
            return self.user
        else:
            response.raise_for_status()

    def load_initial_data(self):
        self.teams = self.get('/users/me/teams')
        self.default_team_id = self.teams[0]['id']
        self.teams_channels_ids = {}
        for team in self.teams:
            self.teams_channels_ids[team['id']] = []
            # get all channels belonging to each team
            for channel in self.get_channels(team['id']):
                self.teams_channels_ids[team['id']].append(channel['id'])

    def create_post(self, user_id, channel_id, message, files=None, pid=""):
        # create_at = int(time.time() * 1000)
        return self.post(
            '/posts',
            {
                'channel_id': channel_id,
                'message': message,
                'filenames': files or [],
                'root_id': pid,
            })

    def update_post(self, message_id, user_id, channel_id,
                    message, files=None, pid=""):
        return self.post(
            '/posts/%s' % message_id,
            {
                'message': message,
            })

    def channel(self, channel_id):
        channel = {'channel': self.get('/channels/{}'.format(channel_id))}
        return channel

    def get_team_by_name(self, team_name):
        return self.get('/teams/name/{}'.format(team_name))

    def get_channel_by_name(self, channel_name, team_id=None):
        return self.get('/teams/{}/channels/name/{}'.format(
            team_id, channel_name))

    def get_channels(self, team_id=None):
        if team_id is None:
            team_id = self.default_team_id
        return self.get('/users/me/teams/{}/channels'.format(team_id))

    def create_user_dict(self, v4_dict):
        new_dict = {}
        new_dict[v4_dict['id']] = v4_dict
        return new_dict

    def get_user_info(self, user_id):
        return self.get('/users/{}'.format(user_id))

    def hooks_list(self):
        return self.get('/hooks/incoming')

    def hooks_create(self, **kwargs):
        return self.post(
            '/hooks/incoming', kwargs)

    def hooks_get(self, webhook_id):
        return self.get(
            '/hooks/incoming/{}'.format(webhook_id))

    def hooks_delete(self, webhook_id):
        response = self.delete('/hooks/incoming/{}'.format(webhook_id))
        if response['status_code'] == 404:
            raise Exception('API_NOT_FOUND',
                            'The API /api/v4/hooks/incoming/{hook_id} '
                            'might not be supported by your server.')
        return response

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

    def get_file_link(self, file_id):
        return self.get('/files/{}/link'.format(file_id))


class MattermostClientv4(MattermostClient):

    def __init__(self, url, team, email, password, ssl_verify=True, login=1):
        self.users = {}
        self.channels = {}
        self.mentions = {}
        self.api = MattermostAPIv4(url, ssl_verify)
        self.user = None
        self.info = None
        self.websocket = None
        self.email = None
        self.team = team
        self.email = email
        self.password = password

        if login:
            self.login(team, email, password)

    def connect_websocket(self):
        host = self.api.url.replace('http', 'ws').replace('https', 'wss')
        url = host + '/websocket'
        self._connect_websocket(url, cookie_name='MMAUTHTOKEN')
        return self.websocket.getstatus() == 101
