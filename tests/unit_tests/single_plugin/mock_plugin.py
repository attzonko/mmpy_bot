from mmpy_bot.utils import allow_only_direct_message
from mmpy_bot.utils import allowed_users
from mmpy_bot.bot import respond_to
from tests.behavior_tests.driver_settings import BOT_NAME, BOT_LOGIN

@respond_to('^admin$')
@allow_only_direct_message()
@allowed_users(BOT_NAME, BOT_LOGIN)
def mock_users_access(message):
    message.reply('Access allowed!')


@respond_to('file$')
def get_timestamp_file(message):
    file = open('new.txt', 'w+')
    result = message.upload_file(file)
    file.close()
    if 'file_infos' not in result:
        message.reply('upload file error')
    file_id = result['file_infos'][0]['id']
    message.reply('hello', [file_id])
