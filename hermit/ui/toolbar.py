from .base import DeadTime
import hermit.ui.state as state


bar_len = DeadTime // 4
chars = ["#", "=", "-", "."]
Bars = [chars[0] * (bar_len - 1) + char + " " * bar_len for char in chars]


def bottom_toolbar():
    """Renders the bottom toolbar."""
    debug_status = ""
    testnet_status = ""
    wallet_status = ""

    if state.Debug:
        debug_status = "DEBUG"

    if state.Testnet:
        testnet_status = "TESTNET"

    b = DeadTime - state.Timeout
    if state.Wallet.unlocked():
        bar = Bars[b % 4][b // 4 : b // 4 + bar_len]
        wallet_status = "wallet UNLOCKED " + bar
    else:
        wallet_status = "wallet locked"

    return "Hermit --- {0:<32} {1:>7} {2:>5}".format(
        wallet_status, testnet_status, debug_status
    )
