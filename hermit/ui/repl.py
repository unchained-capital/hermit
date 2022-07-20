import traceback


from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout

from typing import Dict

from .base import DeadTime
from .toolbar import bottom_toolbar

from hermit.errors import HermitError
import hermit.ui.state as state

Bindings = KeyBindings()


def repl(commands: Dict, mode: str = "", help_command=None):
    """Start a REPL with the given `commands`, `mode`, and `help_command`."""
    commandCompleter = WordCompleter(
        [c for c in commands], sentence=True  # allows hyphens
    )

    oldSession = state.Session
    state.Session = PromptSession(
        key_bindings=Bindings, bottom_toolbar=bottom_toolbar, refresh_interval=0.1
    )
    state.Wallet.shards.interface.options = {"bottom_toolbar": bottom_toolbar}
    done = None
    with patch_stdout():
        while not done:
            try:
                unlocked = " "
                if state.Wallet.unlocked():
                    unlocked = "*"
                command_line = state.Session.prompt(
                    HTML("<b>{}{}></b> ".format(unlocked, mode)),
                    completer=commandCompleter,
                ).split()

                if len(command_line) == 0:
                    continue

                if command_line[0] in commands:
                    command_fn = commands[command_line[0]]
                    try:
                        done = command_fn(*(command_line[1:]))
                    except HermitError as e:
                        print(e)
                        # If we get a HermitError here, it generally means that someone
                        # didnt provide the right kinds of arguments to a command line
                        # so we should show them some help.
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
                continue
    state.Session = oldSession


@Condition
def check_timer():
    state.Live = True
    if state.Wallet.unlocked():
        state.Timeout = DeadTime
    return False


@Bindings.add("<any>", filter=check_timer)
def escape_binding(event):
    pass


@Bindings.add("`", eager=True)
def force_check_timer(event):
    check_timer()


@Bindings.add("escape", eager=True)
def force_lock(event):
    state.Wallet.lock()
