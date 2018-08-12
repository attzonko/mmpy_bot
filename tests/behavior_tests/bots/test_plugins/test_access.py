# -*- encoding: utf-8 -*-

from mmpy_bot.utils import allowed_users
from mmpy_bot.bot import respond_to

import sys
import os
sys.path.append(os.getcwd()) # enable importing driver_settings

from tests.behavior_tests.bots import driver_settings


@respond_to('^allowed_driver$')
@allowed_users(driver_settings.BOT_NAME)
def driver_allowed_hello(message):
    message.reply('Driver allowed!')


@respond_to('^not_allowed_driver$')
@allowed_users('somebody-not-driver')
def driver_not_allowed_hello(message):
    message.reply('Driver not allowed!')
