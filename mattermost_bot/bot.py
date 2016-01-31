# -*- coding: utf-8 -*-

from __future__ import absolute_import

import imp
import importlib
import logging
import os
import re
import time
from glob import glob

from six.moves import _thread

from mattermost_bot import settings
from mattermost_bot.dispatcher import MessageDispatcher
from mattermost_bot.mattermost import MattermostClient

logger = logging.getLogger(__name__)


class Bot(object):
    def __init__(self):
        self._client = MattermostClient(
            settings.BOT_URL, settings.BOT_TEAM,
            settings.BOT_LOGIN, settings.BOT_PASSWORD,
        )
        logger.info('connected to mattermost')
        self._plugins = PluginsManager()
        self._dispatcher = MessageDispatcher(self._client, self._plugins)

    def run(self):
        self._plugins.init_plugins()
        self._dispatcher.start()
        _thread.start_new_thread(self._keep_active, tuple())
        self._dispatcher.loop()

    def _keep_active(self):
        logger.info('keep active thread started')
        while True:
            time.sleep(60)
            self._client.ping()


class PluginsManager(object):
    commands = {
        'respond_to': {},
        'listen_to': {}
    }

    def __init__(self):
        pass

    def init_plugins(self):
        if hasattr(settings, 'PLUGINS'):
            plugins = settings.PLUGINS
        else:
            plugins = 'mattermost_bot.plugins'

        for plugin in plugins:
            self._load_plugins(plugin)

    @staticmethod
    def _load_plugins(plugin):
        logger.info('loading plugin "%s"', plugin)
        path_name = None
        for mod in plugin.split('.'):
            if path_name is not None:
                path_name = [path_name]
            _, path_name, _ = imp.find_module(mod, path_name)
        for py_file in glob('{}/[!_]*.py'.format(path_name)):
            module = '.'.join((plugin, os.path.split(py_file)[-1][:-3]))
            try:
                _module = importlib.import_module(module)
                if hasattr(_module, 'on_init'):
                    _module.on_init()
            except Exception as err:
                logger.exception(err)

    def get_plugins(self, category, text):
        has_matching_plugin = False
        for matcher in self.commands[category]:
            m = matcher.search(text)
            if m:
                has_matching_plugin = True
                yield self.commands[category][matcher], m.groups()

        if not has_matching_plugin:
            yield None, None


def respond_to(regexp, flags=0):
    def wrapper(func):
        PluginsManager.commands['respond_to'][re.compile(regexp, flags)] = func
        logger.info(
            'registered respond_to plugin "%s" to "%s"', func.__name__, regexp)
        return func

    return wrapper


def listen_to(regexp, flags=0):
    def wrapper(func):
        PluginsManager.commands['listen_to'][re.compile(regexp, flags)] = func
        logger.info(
            'registered listen_to plugin "%s" to "%s"', func.__name__, regexp)
        return func

    return wrapper
