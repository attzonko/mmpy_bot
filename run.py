#!/usr/bin/env python

import logging
import logging.config
import sys

from mattermost_bot import settings
from mattermost_bot.bot import Bot


def main():
    kw = {
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG if settings.DEBUG else logging.INFO,
        'stream': sys.stdout,
    }
    logging.basicConfig(**kw)

    bot = Bot()
    bot.run()


if __name__ == '__main__':
    main()
