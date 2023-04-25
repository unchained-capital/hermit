from typing import Dict
from functools import wraps
from ..config import get_config

# from hermit.errors import HermitError

#: Duration of idle time before the wallet will automatically lock
#: itself.
DeadTime = get_config().coordinator["relock_timeout"]


def clear_screen() -> None:
    """Clears the screen."""
    print(chr(27) + "c")


def command(name: str, commands: Dict):
    """Decorator for defining a new command."""

    def _command_decorator(f):
        nonlocal name
        if name is None:
            name = f.name
        if name in commands:
            raise Exception("command already defined: " + name)

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        commands[name] = wrapper

        return wrapper

    return _command_decorator


def disabled(*args, **kwargs):
    """command disabled"""
    print("Command disabled.")


def disabled_command(name: str, commands: Dict):
    """Decorator for defining a new command."""

    def _command_decorator(f):
        nonlocal name
        if name is None:
            name = f.name
        if name in commands:
            raise Exception("command already defined: " + name)

        @wraps(f)
        def wrapper(*args, **kwargs):
            return disabled(*args, **kwargs)

        return wrapper

    return _command_decorator
