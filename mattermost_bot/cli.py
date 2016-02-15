# -*- coding: utf-8 -*-
import sys
import logging

from mattermost_bot import bot, settings


def main():
    logging.basicConfig(**{
        'format': '[%(asctime)s] %(message)s',
        'datefmt': '%m/%d/%Y %H:%M:%S',
        'level': logging.DEBUG if settings.DEBUG else logging.INFO,
        'stream': sys.stdout,
    })

    try:
        b = bot.Bot()
        b.run()
    except KeyboardInterrupt:
        pass
