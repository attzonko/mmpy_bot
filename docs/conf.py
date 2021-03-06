# -*- coding: utf-8 -*-

import os

from mmpy_bot import __version__

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.todo"]
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
project = "mmpy_bot"
copyright = "2016, "
version = __version__
release = __version__
exclude_patterns = []
pygments_style = "sphinx"
html_theme = "default"
htmlhelp_basename = "mmpy_botdoc"
latex_documents = [
    ("index", "mmpy_bot.tex", "mmpy_bot Documentation", "", "manual"),
]
man_pages = [("index", "mmpy_bot", "mmpy_bot Documentation", ["gotlium"], 1)]
texinfo_documents = [
    (
        "index",
        "mmpy_bot",
        "Mattermost-bot Documentation",
        "gotlium",
        "mmpy_bot",
        "One line description of project.",
        "Miscellaneous",
    ),
]
