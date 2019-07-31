import asyncio

from .base import *
import hermit.ui.state as state

async def relock_wallet_if_timed_out():
    while True:
        await asyncio.sleep(0.5)
        await _handle_tick()

async def _handle_tick():
    global Timeout
    global Live
    global Wallet
    if state.Live:
        state.Live = False
    elif state.Wallet.unlocked() and state.Timeout > 0:
        state.Timeout = state.Timeout - 1
        if state.Timeout <= 0:
            state.Timeout = 0
            state.Wallet.lock()
