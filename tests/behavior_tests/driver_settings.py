import os

PLUGINS = [
]

BOT_URL = os.environ.get("BOT_URL", 'http://SERVER_HOST_DN/api/v4')
BOT_LOGIN = os.environ.get("DRIVERBOT_LOGIN", 'driverbot@mail')
BOT_NAME = os.environ.get("DRIVERBOT_NAME", 'driverbot_name')
BOT_PASSWORD = os.environ.get("DRIVERBOT_PASSWORD", 'driverbot_password')

# this team name should be the same as in driver_settings
BOT_TEAM = os.environ.get("BOT_TEAM", 'default_team_name')

# default public channel name
BOT_CHANNEL = os.environ.get("BOT_CHANNEL", 'off-topic')

# a private channel in BOT_TEAM
BOT_PRIVATE_CHANNEL = os.environ.get("BOT_PRIVATE_CHANNEL", 'test')

SSL_VERIFY = True
