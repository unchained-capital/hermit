from typing import Dict
from functools import wraps

from hermit.errors import HermitError
from hermit.qrcode import displayer, reader

DeadTime = 30

def clear_screen():
    print(chr(27) + "[2J")

# is this even used?
def reset_screen():
    print(chr(27) + "c")

def command(name, commands:Dict):
    def _command_decorator(f):
        nonlocal name
        if name is None:
            name = f.name
        if name in commands:
            raise Exception('command already defined: '+name)

        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except TypeError as terr:
                raise terr
            except Exception as err:
                print(err)
                raise HermitError("Hmm. Something went wrong.")

        commands[name] = wrapper

        return wrapper

    return _command_decorator
