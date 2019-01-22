# -*- encoding: utf-8 -*-

from mmpy_bot.bot import respond_to, listen_to


@respond_to('^!info$')
@listen_to('^!info$')
def info_request(message):
    message.send('TEAM-ID: `%s`' % message.get_team_id())
    message.send('USERNAME: `%s`' % message.get_username())
    message.send('EMAIL: `%s`' % message.get_user_mail())
    message.send('USER-ID: `%s`' % message.get_user_id())
    message.send('IS-DIRECT: %s' % repr(message.is_direct_message()))
    message.send('MENTIONS: %s' % repr(message.get_mentions()))
    message.send('MESSAGE: %s' % message.get_message())
