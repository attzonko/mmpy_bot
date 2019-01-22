# -*- encoding: utf-8 -*-

from mmpy_bot.utils import allowed_users
from mmpy_bot.utils import allowed_channels
from mmpy_bot.bot import respond_to

import sys
import os
sys.path.append(os.getcwd())  # enable importing driver_settings

from tests.behavior_tests.bots import driver_settings   # noqa: E402


@respond_to('^allowed_driver$')
@allowed_users(driver_settings.BOT_NAME)
def driver_allowed_hello(message):
    message.reply('Driver allowed!')


@respond_to('^not_allowed_driver$')
@allowed_users('somebody-not-driver')
def driver_not_allowed_hello(message):
    message.reply('Driver not allowed!')


@respond_to('^allowed_driver_by_email$')
@allowed_users(driver_settings.BOT_LOGIN)
def driver_allowed_hello_by_email(message):
    message.reply('Driver email allowed!')


@respond_to('^allowed_channel$')
@allowed_channels(driver_settings.BOT_PRIVATE_CHANNEL)
def driver_allowed_chan(message):
    message.reply('Driver in channel allowed!')


@respond_to('^not_allowed_channel$')
@allowed_channels(driver_settings.BOT_CHANNEL)
def driver_not_allowed_chan(message):
    message.reply('Driver in channel NOT allowed!')
