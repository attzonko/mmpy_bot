# -*- encoding: utf-8 -*-

from mattermost_bot.utils import allowed_users
from mattermost_bot.bot import respond_to


@respond_to('^admin$')
@allowed_users('admin', 'root')
def hello_react(message):
    message.reply('Access allowed!')
