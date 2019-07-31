from .base import *
from .wallet import wallet_command
from .shards import shard_command
import hermit.ui.state as state

@wallet_command('unlock')
@shard_command('unlock')
def unlock():
    """usage:  unlock

  Explicity unlock the wallet, prompting for shard passwords.

  Many commands will do this implicitly.

    """
    state.Wallet.unlock()
    if state.Wallet.unlocked:
        state.Timeout = DeadTime


@wallet_command('lock')
@shard_command('lock')
def lock():
    """usage:  lock

  Explicity lock the wallet, requiring passwords to be re-entered as
  necessary.

  The wallet will automatically lock after 30 seconds.

    """
    state.Wallet.lock()

@shard_command('clear')
@wallet_command('clear')
def clear():
    """usage:  clear

  Clear screen.
    """
    clear_screen()

@wallet_command('debug')
@shard_command('debug')
def toggle_debug():
    """usage:  debug

  Toggle debug mode on or off.

  When debug mode is active, more information is displayed about
  errors and some additional commands are available.

  The word DEBUG will also appear in Hermit's bottom toolbar.

    """
    state.Debug = not state.Debug
