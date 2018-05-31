# -*- encoding: utf-8 -*-

from mmpy_bot.utils import allow_only_direct_message
from mmpy_bot.utils import allowed_users
from mmpy_bot.bot import respond_to


@respond_to('^admin$')
@allow_only_direct_message()
@allowed_users('admin', 'root')
def users_access(message):
    message.reply('Access allowed!')
