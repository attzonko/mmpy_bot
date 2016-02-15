# -*- coding: utf-8 -*-

import os

from mattermost_bot import get_version

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.todo']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'mattermost_bot'
copyright = u'2016, '
version = get_version()
release = get_version()
exclude_patterns = []
pygments_style = 'sphinx'
html_theme = 'default'
htmlhelp_basename = 'mattermost_botdoc'
latex_documents = [
    ('index', 'mattermost_bot.tex', u'mattermost_bot Documentation',
     u'', 'manual'),
]
man_pages = [
    ('index', 'mattermost_bot', u'mattermost_bot Documentation',
     [u'gotlium'], 1)
]
texinfo_documents = [
    ('index', 'mattermost_bot', u'Mattermost-bot Documentation',
     u'gotlium', 'mattermost_bot', 'One line description of project.',
     'Miscellaneous'),
]
