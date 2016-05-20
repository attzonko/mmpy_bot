# -*- coding: utf-8 -*-

from __future__ import absolute_import

import importlib
import traceback
import logging
import re

from six import iteritems

from mattermost_bot.utils import WorkerPool
from mattermost_bot import settings

logger = logging.getLogger(__name__)

MESSAGE_MATCHER = re.compile(r'^(@.*?\:?)\s(.*)', re.MULTILINE | re.DOTALL)
BOT_ICON = settings.BOT_ICON if hasattr(settings, 'BOT_ICON') else None
BOT_EMOJI = settings.BOT_EMOJI if hasattr(settings, 'BOT_EMOJI') else None


class MessageDispatcher(object):
    def __init__(self, client, plugins):
        self._client = client
        self._pool = WorkerPool(self.dispatch_msg, settings.WORKERS_NUM)
        self._plugins = plugins
        self._channel_info = {}

    def start(self):
        self._pool.start()

    @staticmethod
    def get_message(msg):
        return msg.get(
            'props', {}).get('post', {}).get('message', '').strip()

    def ignore(self, _msg):
        msg = self.get_message(_msg)
        for prefix in settings.IGNORE_NOTIFIES:
            if msg.startswith(prefix):
                return True

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
                    func(Message(self._client, msg, self._pool), *args)
                except Exception as err:
                    logger.exception(err)
                    reply = '[%s] I have problem when handling "%s"\n' % (
                        func.__name__, text)
                    reply += '```\n%s\n```' % traceback.format_exc()
                    self._client.channel_msg(msg['channel_id'], reply)

        if not responded and category == 'respond_to':
            if settings.DEFAULT_REPLY_MODULE is not None:
                mod = importlib.import_module(settings.DEFAULT_REPLY_MODULE)
                if hasattr(mod, 'default_reply'):
                    return getattr(mod, 'default_reply')(self, msg)
            self._default_reply(msg)

    def _on_new_message(self, msg):
        if self.ignore(msg) is True:
            return

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
        if settings.DEFAULT_REPLY:
            return self._client.channel_msg(
                msg['channel_id'], settings.DEFAULT_REPLY)

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

    def __init__(self, client, body, pool):
        from mattermost_bot.bot import PluginsManager

        self._plugins = PluginsManager()
        self._client = client
        self._body = body
        self._pool = pool

    def get_user_info(self, key, user_id=None):
        user_id = user_id or self._body['user_id']
        if not Message.users or user_id not in Message.users:
            Message.users = self._client.get_users()
        return Message.users[user_id].get(key)

    def get_username(self, user_id=None):
        return self.get_user_info('username', user_id)

    def get_user_mail(self, user_id=None):
        return self.get_user_info('email', user_id)

    def get_user_id(self, user_id=None):
        return self.get_user_info('id', user_id)

    def get_channel_name(self, channel_id=None):
        channel_id = channel_id or self._body['channel_id']
        if channel_id in self.channels:
            channel_name = self.channels[channel_id]
        else:
            channel = self._client.api.channel(channel_id)
            channel_name = channel['channel']['name']
            self.channels[channel_id] = channel_name
        return channel_name

    def get_team_id(self):
        return self._client.api.team_id

    def get_message(self):
        return self._body['props']['post']['message'].strip()

    def is_direct_message(self):
        return self._body['message_type'] == 'D'

    def get_busy_workers(self):
        return self._pool.get_busy_workers()

    def get_mentions(self):
        return self._body['props'].get('mentions')

    def _gen_at_message(self, text):
        return '@{}: {}'.format(self.get_username(), text)

    def _gen_reply(self, text):
        if self._body['message_type'] == '?':
            return self._gen_at_message(text)
        return text

    def _get_first_webhook(self):
        hooks = self._client.api.hooks_list()
        if not hooks:
            for channel in self._client.api.get_channels():
                if channel.get('name') == 'town-square':
                    return self._client.api.hooks_create(
                        channel_id=channel.get('id')).get('id')
        return hooks[0].get('id')

    @staticmethod
    def _get_webhook_url_by_id(hook_id):
        base = '/'.join(settings.BOT_URL.split('/')[:3])
        return '%s/hooks/%s' % (base, hook_id)

    def reply_webapi(self, text, *args, **kwargs):
        self.send_webapi(self._gen_reply(text), *args, **kwargs)

    def send_webapi(self, text, attachments=None, channel_id=None, **kwargs):
        url = self._get_webhook_url_by_id(self._get_first_webhook())
        kwargs['username'] = kwargs.get(
            'username', self.get_username(self._client.user['id']))
        kwargs['icon_url'] = kwargs.get('icon_url', BOT_ICON)
        kwargs['icon_emoji'] = kwargs.get('icon_emoji', BOT_EMOJI)
        self._client.api.in_webhook(
            url, self.get_channel_name(channel_id), text,
            attachments=attachments, **kwargs)

    def reply(self, text):
        self.send(self._gen_reply(text))

    def send(self, text, channel_id=None):
        self._client.channel_msg(channel_id or self._body['channel_id'], text)

    def react(self, emoji_name):
        self._client.channel_msg(
            self._body['channel_id'], emoji_name,
            pid=self._body['props']['post']['id'])

    def comment(self, message):
        self.react(message)

    def docs_reply(self, docs_format='    • `{0}` {1}'):
        reply = [docs_format.format(v.__name__, v.__doc__ or "")
                 for p, v in iteritems(self._plugins.commands['respond_to'])]
        return '\n'.join(reply)

    @property
    def channel(self):
        return self._body['channel_id']

    @property
    def body(self):
        return self._body
