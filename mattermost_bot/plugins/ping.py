# -*- coding: utf-8 -*-

from mattermost_bot.bot import respond_to
import re


@respond_to('ping', re.IGNORECASE)
def ping_reply(message):
    message.reply('pong')
ping_reply.__doc__ = "Send pong"
