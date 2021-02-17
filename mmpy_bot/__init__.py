"""A python based chat bot for [Mattermost](http://www.mattermost.org)."""
VERSION = (1, 3, 8)


def get_version():
    return '.'.join(map(str, VERSION))

__version__ = get_version()
