# -*- coding: utf-8 -*-

import time

from mmpy_bot.bot import respond_to


@respond_to('sleep (.*)')
def sleep_reply(message, sec):
    message.reply('Ok, I will be waiting %s sec' % sec)
    time.sleep(int(sec))
    message.reply('done')


sleep_reply.__doc__ = "Sleep time"
