# -*- encoding: utf-8 -*-

from mmpy_bot.bot import respond_to, listen_to
import re

import sys
import os
sys.path.append(os.getcwd())  # path to get files


@respond_to('^show_me_src$', re.IGNORECASE)
@listen_to('^show_me_src$', re.IGNORECASE)
def responde_mysrc(message):

    with open(os.sep.join(
              ['tests', 'behavior_tests', 'bots', 'responder.py']),
              'r') as f:
        result = message.upload_file(f)
        if 'file_infos' not in result:
            message.reply('upload file error')
        file_id = result['file_infos'][0]['id']
        message.reply('my source:', [file_id])
