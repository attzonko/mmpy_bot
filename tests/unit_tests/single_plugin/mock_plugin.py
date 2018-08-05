from mmpy_bot.utils import allow_only_direct_message
from mmpy_bot.utils import allowed_users
from mmpy_bot.bot import respond_to
from tests.behavior_tests.driver_settings import BOT_NAME, BOT_LOGIN

@respond_to('^admin$')
@allow_only_direct_message()
@allowed_users(BOT_NAME, BOT_LOGIN)
def mock_users_access(message):
    message.reply('Access allowed!')
