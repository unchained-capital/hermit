from typing import Dict
from functools import wraps

# from hermit.errors import HermitError

#: Duration of idle time before the wallet will automatically lock
#: itself.
DeadTime = 60


def clear_screen() -> None:
    """Clears the screen."""
    print(chr(27) + "[2J")


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
