from os import listdir
from os.path import exists, join

from .config import get_config

_PluginsLoaded = frozenset()


def load_plugins():
    global _PluginsLoaded
    _plugin_dir = get_config().paths["plugin_dir"]
    plugins_loaded = []
    if exists(_plugin_dir):
        for basename in listdir(_plugin_dir):
            if basename.endswith(".py"):
                print(f"Loading plugin {basename} ...")
                exec(open(join(_plugin_dir, basename), "r").read())
                plugins_loaded.append(basename)
    _PluginsLoaded = frozenset(plugins_loaded)


def plugins_loaded():
    return _PluginsLoaded
