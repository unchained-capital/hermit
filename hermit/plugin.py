from os import listdir
from os.path import exists, join

from hermit.config import HermitConfig

PluginsLoaded = []

_config =  HermitConfig.load()
if exists(_config.plugin_dir):
    for basename in listdir(_config.plugin_dir):
        if basename.endswith('.py'):
            # FIXME this doesn't feel right
            PluginsLoaded.append(basename)
            print("Loading plugin {}".format(basename))
            exec(open(join(_config.plugin_dir, basename), 'r').read())
