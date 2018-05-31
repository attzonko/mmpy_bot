# -*- coding: utf-8 -*-

import re

from mmpy_bot.bot import respond_to


@respond_to('^busy|jobs$', re.IGNORECASE)
def busy_reply(message):
    busy = message.get_busy_workers() - 1
    message.reply('Num of busy workers is `%d`' % busy)


busy_reply.__doc__ = "Show num of busy workers"
