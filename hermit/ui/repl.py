import asyncio
import traceback


from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout

from .base import *
from .toolbar import *
import hermit.ui.state as state

Bindings = KeyBindings()

def repl(commands:Dict, mode="", help_command=None):
    commandCompleter = WordCompleter([c for c in commands])

    oldSession = state.Session
    state.Session = PromptSession(key_bindings=Bindings,
                            bottom_toolbar=bottom_toolbar,
                            refresh_interval=0.1)
    state.Wallet.shards.interface.options = {'bottom_toolbar': bottom_toolbar}
    done = None
    with patch_stdout():
        while not done:
            try:
                unlocked = ' '
                if state.Wallet.unlocked():
                    unlocked = '*'
                command_line = state.Session.prompt('{}{}> '.format(unlocked, mode),
                                              completer=commandCompleter,
                                              ).split()

                if len(command_line) == 0:
                    continue

                if command_line[0] in commands:
                    command_fn = commands[command_line[0]]
                    try:
                        done = command_fn(*(command_line[1:]))
                    except TypeError as err:
                        if state.Debug:
                            raise err
                        if help_command is not None:
                            help_command(command_line[0])
                else:
                    raise HermitError("Unknown command")

            except KeyboardInterrupt:
                continue
            except HermitError as e:
                print(e)
                if state.Debug:
                    traceback.print_exc()
                continue
            except EOFError:
                break
            except Exception as err:
                print(err)
                if state.Debug:
                    traceback.print_exc()
                break
    state.Session = oldSession


@Condition
def check_timer():
    state.Live = True
    if state.Wallet.unlocked():
        state.Timeout = DeadTime
    return False


@Bindings.add('<any>', filter=check_timer)
def escape_binding(event):
    pass


@Bindings.add('`', eager=True)
def force_check_timer(event):
    check_timer()


@Bindings.add('escape', eager=True)
def force_lock(event):
    state.Wallet.lock()
