# -*- coding: utf-8 -*-

import re

from mmpy_bot.bot import respond_to


@respond_to('^ping$', re.IGNORECASE)
def ping_reply(message):
    message.reply('pong')


ping_reply.__doc__ = "Send pong"
