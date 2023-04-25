from typing import Optional
from os import environ

from prompt_toolkit import PromptSession

from hermit.wallet import HDWallet

Timeout = 0

Live = False

#: Whether the wallet is in DEBUG mode or not.
#:
#:
#: Defaults to ON if the `DEBUG` environment variable is set on Hermit
#: launch.
#:
#: Can be explicitly toggled using the `debug` command.
Debug = "DEBUG" in environ

#: Whether the wallet is in testnet mode or not.
#:
#: Defaults to testnet if the `TESTNET` environment variable is set on
#: Hermit launch.
#:
#: Can be explicitly toggled using the `testnet` command.
Testnet = "TESTNET" in environ

#: The current wallet instance.
Wallet = HDWallet()

Session: Optional[PromptSession] = None
