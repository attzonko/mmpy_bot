import re

from mmpy_bot.bot import listen_to
from mmpy_bot.bot import respond_to


@respond_to('picture$', re.IGNORECASE)
@listen_to('picture$', re.IGNORECASE)
def get_file_public_link(message):
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
