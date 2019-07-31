import asyncio

from .base import *
import hermit.ui.state as state

Bars = '#'*DeadTime + ' '*DeadTime

def bottom_toolbar():
    debug_status = ""
    testnet_status = ""
    wallet_status = ""

    if state.Debug:
        debug_status = "DEBUG"

    if state.Testnet:
        testnet_status = "TESTNET"

    b = DeadTime - state.Timeout
    if state.Wallet.unlocked():
        wallet_status = "wallet UNLOCKED " + Bars[b:b+DeadTime]
    else:
        wallet_status = "wallet locked"

    return "Hermit --- {0:<16} {1:>10} {2:>8}".format(wallet_status,
                                                      testnet_status,
                                                      debug_status)
