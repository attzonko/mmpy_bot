# -*- encoding: utf-8 -*-

from mmpy_bot.bot import respond_to, listen_to


@respond_to('^!help$')
@listen_to('^!help$')
def help_request(message):
    message.send(message.docs_reply())
