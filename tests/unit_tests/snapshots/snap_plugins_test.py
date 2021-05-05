# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots[
    "TestPlugin.test_help_string 1"
] = """Plugin FakePlugin has the following functions:
----
- `^click_command (.*)?`:
        Usage: click_command [OPTIONS]
        
          Help string for the entire function.
        
        Options:
          --option INTEGER  Help string for the optional argument.
          --help            Show this message and exit.
----
- `direct_pattern`:
        No description provided.
    Additional information:
    - Needs to be a direct message.
    - Restricted to certain users.
----
- `^!help$`:
        Prints the list of functions registered on every active plugin.
----
- `^help$`:
        Prints the list of functions registered on every active plugin.
    Additional information:
    - Needs to either mention @ or be a direct message.
----
- `async_pattern`:
        Async function docstring.
----
- `another_async_pattern`:
        Async function docstring.
    Additional information:
    - Needs to be a direct message.
----
- `pattern`:
        This is the docstring of my_function.
----
### Registered webhooks:
- `webhook_id`:
        A webhook function.
"""

snapshots[
    "TestPlugin.test_no_help_trigger 1"
] = """Plugin FakePlugin has the following functions:
----
- `^click_command (.*)?`:
        Usage: click_command [OPTIONS]
        
          Help string for the entire function.
        
        Options:
          --option INTEGER  Help string for the optional argument.
          --help            Show this message and exit.
----
- `direct_pattern`:
        No description provided.
    Additional information:
    - Needs to be a direct message.
    - Restricted to certain users.
----
- `async_pattern`:
        Async function docstring.
----
- `another_async_pattern`:
        Async function docstring.
    Additional information:
    - Needs to be a direct message.
----
- `pattern`:
        This is the docstring of my_function.
----
### Registered webhooks:
- `webhook_id`:
        A webhook function.
"""
