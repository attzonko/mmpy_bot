# -*- coding: utf-8 -*-

import re

from mmpy_bot.bot import listen_to
from mmpy_bot.bot import respond_to


@respond_to('hello$', re.IGNORECASE)
def hello_reply(message):
    message.reply('hello sender!')


@respond_to('hello_formatting')
@listen_to('hello_formatting$')
def hello_reply_formatting(message):
    # Format message with italic style
    message.reply('_hello_ sender!')


@listen_to('hello$')
def hello_send(message):
    message.send('hello channel!')

@listen_to('hello$')
def hello_send_alternative(message):
    message.send('hello channel!')

@listen_to('hello_decorators')
@respond_to('hello_decorators')
def hello_decorators(message):
    message.send('hello!')


@respond_to('hello_web_api', re.IGNORECASE)
def web_api_reply(message):
    attachments = [{
        'fallback': 'Fallback text',
        'author_name': 'Author',
        'author_link': 'http://www.github.com',
        'text': 'Some text here ...',
        'color': '#59afe1'
    }]
    message.reply_webapi(
        'Attachments example', attachments,
        username='Mattermost-Bot',
        icon_url='https://goo.gl/OF4DBq',
    )


@listen_to('hello_comment', re.IGNORECASE)
def hello_comment(message):
    message.comment('some comments ...')


@listen_to('hello_react', re.IGNORECASE)
def hello_react(message):
    message.react(':+1:')
    
@listen_to('picture$', re.IGNORECASE)
def search_picture(message):
    # check if have file
    if 'image' not in message.body['data']:
        message.reply('no pic file!')
        return
    # handle the first file, get file public link
    file_id = message.body['data']['post']['file_ids'][0]
    file_link = message.get_file_link(file_id)
    if 'link' not in file_link:
        message.reply(file_link['message'])
        return
    file_link = file_link['link']
    message.reply(file_link)
