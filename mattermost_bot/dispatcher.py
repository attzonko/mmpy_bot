# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import re
import traceback

from six import iteritems

from mattermost_bot.utils import WorkerPool
from mattermost_bot import settings

logger = logging.getLogger(__name__)

MESSAGE_MATCHER = re.compile(r'^(@.*?\:?)\s(.*)', re.MULTILINE | re.DOTALL)


class MessageDispatcher(object):
    def __init__(self, client, plugins):
        self._client = client
        self._pool = WorkerPool(self.dispatch_msg)
        self._plugins = plugins
        self._channel_info = {}

    def start(self):
        self._pool.start()

    @staticmethod
    def get_message(msg):
        return msg.get(
            'props', {}).get('post', {}).get('message', '').strip()

    def is_mentioned(self, msg):
        mentions = msg.get('props', {}).get('mentions', [])
        return self._client.user['id'] in mentions

    def is_personal(self, msg):
        channel_id = msg['channel_id']
        if channel_id in self._channel_info:
            channel_type = self._channel_info[channel_id]
        else:
            channel = self._client.api.channel(channel_id)
            channel_type = channel['channel']['type']
            self._channel_info[channel_id] = channel_type
        return channel_type == 'D'

    def dispatch_msg(self, msg):
        category = msg[0]
        msg = msg[1]
        text = self.get_message(msg)
        responded = False
        msg['message_type'] = '?'
        if self.is_personal(msg):
            msg['message_type'] = 'D'
        for func, args in self._plugins.get_plugins(category, text):
            if func:
                responded = True
                try:
                    func(Message(self._client, msg), *args)
                except Exception as err:
                    logger.exception(err)
                    reply = '[%s] I have problem when handling "%s"\n' % (
                        func.__name__, text)
                    reply += '```\n%s\n```' % traceback.format_exc()
                    self._client.channel_msg(msg['channel_id'], reply)

        if not responded and category == 'respond_to':
            self._default_reply(msg)

    def _on_new_message(self, msg):
        msg = self.filter_text(msg)
        if self.is_mentioned(msg) or self.is_personal(msg):
            self._pool.add_task(('respond_to', msg))
        else:
            self._pool.add_task(('listen_to', msg))

    def filter_text(self, msg):
        text = self.get_message(msg)
        if self.is_mentioned(msg):
            m = MESSAGE_MATCHER.match(text)
            if m:
                msg['props']['post']['message'] = m.group(2).strip()
        return msg

    def loop(self):
        for self.event in self._client.messages(True, 'posted'):
            self._on_new_message(self.event)

    def _default_reply(self, msg):
        default_reply = [
            u'Bad command "%s", You can ask me one of the '
            u'following questions:\n' % self.get_message(msg),
        ]
        docs_fmt = u'{1}' if settings.PLUGINS_ONLY_DOC_STRING else u'`{0}` {1}'

        default_reply += [
            docs_fmt.format(p.pattern, v.__doc__ or "")
            for p, v in iteritems(self._plugins.commands['respond_to'])]

        self._client.channel_msg(msg['channel_id'], '\n'.join(default_reply))


class Message(object):
    users = {}
    channels = {}

    def __init__(self, client, body):
        self._client = client
        self._body = body

    def get_user_info(self, key, user_id=None):
        user_id = user_id or self._body['user_id']
        if user_id in Message.users:
            user_info = Message.users[user_id]
        else:
            user_info = self._client.api.user(user_id)
            Message.users[user_id] = user_info
        return user_info.get(key)

    def get_username(self, user_id=None):
        return self.get_user_info('username', user_id)

    def get_user_mail(self, user_id=None):
        return self.get_user_info('email', user_id)

    def get_user_id(self, user_id=None):
        return self.get_user_info('id', user_id)

    def get_channel_name(self):
        channel_id = self._body['channel_id']
        if channel_id in self.channels:
            channel_name = self.channels[channel_id]
        else:
            channel = self._client.api.channel(channel_id)
            channel_name = channel['channel']['name']
            self.channels[channel_id] = channel_name
        return channel_name

    def get_team_id(self):
        return self._client.user.get('team_id')

    def get_message(self):
        return self._body['props']['post']['message'].strip()

    def is_direct_message(self):
        return self._body['message_type'] == 'D'

    def get_mentions(self):
        return self._body['props'].get('mentions')

    def _gen_at_message(self, text):
        return '@{}: {}'.format(self.get_username(), text)

    def _gen_reply(self, text):
        if self._body['message_type'] == '?':
            return self._gen_at_message(text)
        return text

    def reply(self, text):
        self.send(self._gen_reply(text))

    def send(self, text, channel_id=None):
        self._client.channel_msg(channel_id or self._body['channel_id'], text)

    @property
    def channel(self):
        return self._body['channel_id']

    @property
    def body(self):
        return self._body
