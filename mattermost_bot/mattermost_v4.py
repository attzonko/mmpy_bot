import json
import logging
import ssl
import time

import requests
import websocket
import websocket._exceptions

from mattermost_bot.mattermost import MattermostClient, MattermostAPI
from pprint import pprint

logger = logging.getLogger(__name__)

class MattermostAPIv4(MattermostAPI):

    def login(self, team, account, password):
        props = {'login_id': account, 'password': password}
        response =requests.post(
            self.url + '/users/login',
            data = json.dumps(props),
            verify=self.ssl_verify)
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
        create_at = int(time.time() * 1000)
        return self.post(
                    '/posts',
                    {
                        'channel_id': channel_id,
                        'message': message,
                        'filenames': files or [],
                        'root_id': pid,
                    })
    def update_post(self, message_id, user_id, channel_id, message, files=None, pid=""):
        return self.post(
            '/posts/%s' % message_id,
            {
                'message': message,
            })

    def channel(self, channel_id):
        channel = {'channel': self.get('/channels/%s' % channel_id)}
        return channel

    def get_channels(self, team_id=None):
        if team_id is None:
            team_id = self.default_team_id
        return self.get('/users/me/teams/%s/channels' % team_id)

    def create_user_dict(self, v4_dict):
        new_dict = {}
        new_dict[v4_dict['id']]=v4_dict
        return new_dict

    def get_profiles(self,channel_id=None, pagination_size=100):
        profiles = {}
        if channel_id is not None:
            team_id = self.get_team_id(channel_id)
        else:
            team_id = self.default_team_id

        start = 0

        current_page = self.get('/users?page=0&per_page={}&in_team={}'.format(pagination_size, team_id))
        for user in current_page:
            profiles.update(self.create_user_dict(user))

        while len(current_page) == pagination_size:
            start = start + 1
	    current_page = self.get('/users?page={}&per_page={}&in_team={}'.format(start, pagination_size, team_id))
            for user in current_page:
                 profiles.update(self.create_user_dict(user))
        return profiles


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
