from prompt_toolkit.eventloop.defaults import use_asyncio_event_loop
from ..plugins import load_plugins
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
    """Start the Hermit REPL user interface."""
    clear_screen()
    load_plugins()
    print(Banner.format(__version__))
    use_asyncio_event_loop()
    loop = asyncio.get_event_loop()
    loop.create_task(relock_wallet_if_timed_out())  # deadman_task
    wallet_repl()
