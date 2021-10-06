#from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop

from hermit.plugin import PluginsLoaded

from .wallet import clear_screen, wallet_repl
from .relocker import asyncio, relock_wallet_if_timed_out
from hermit import __version__

# HACK to initiate all the commands:
from .common import unlock, lock, clear, toggle_debug, version  # type: ignore  # noqa: F401


Banner = r"""
 _   _                     _ _
| | | |                   (_) |      Command-line, sharded HD wallet
| |_| | ___ _ __ _ __ ___  _| |_       for air-gapped deployments
|  _  |/ _ \ '__| '_ ` _ \| | __|
| | | |  __/ |  | | | | | | | |_     Copyright 2019 Unchained Capital, Inc.
\_| |_/\___|_|  |_| |_| |_|_|\__|    Licensed under Apache 2.0

You are in WALLET mode.  Type 'help' for help.               (v{})
"""


def main():
    clear_screen()
    print(Banner.format(__version__))
    for plugin in PluginsLoaded:
        print("Loaded plugin {}".format(plugin))
    #use_asyncio_event_loop()
    loop = asyncio.get_event_loop()
    loop.create_task(relock_wallet_if_timed_out())  # deadman_task
    loop.run_until_complete(wallet_repl())
