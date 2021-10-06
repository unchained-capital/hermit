import yaml
from os import path, environ
from typing import Dict


class HermitConfig:
    """Object to hold Hermit configuration

    Hermit reads its configuration from a YAML file on disk at
    `/etc/hermit.yaml` (by default).

    The following settings are supported:

    * `shards_file` -- path to store shards
    * `plugin_dir` -- directory containing plugins
    * `commands` -- a dictionary of command lines used to manipulate storage, see :attribute:`hermit.HermitConfig.DefaultCommands`.

    """

    #: Default commands for persistence and backup of data.
    #:
    #:
    #: Each command will have the string `{0}` interpolated with the
    #: path to the file being processed.
    #:
    #: The following commands are defined:
    #:
    #: * `persistShards` -- copy from file system to persistent storage
    #: * `getPersistedShards` -- copy from persistent storage to file system
    #: * `backupShards` -- copy from file system to backup storage
    #: * `restoreBackup` -- copy from backup storage to file system
    #:
    DefaultCommands = {
        "persistShards": "cat {0} | gzip -c - > {0}.persisted",
        "backupShards": "cp {0}.persisted {0}.backup",
        "restoreBackup": "zcat {0}.backup > {0}",
        "getPersistedShards": "zcat {0}.persisted > {0}",
    }

    DefaultPaths = {
        "config_file": "/etc/hermit.yaml",
        "shards_file": "/tmp/shard_words.bson",
        "plugin_dir": "/var/lib/hermit",
    }


    DefaultQRSystem = {
        "type": "opencv",
        "display": "opencv",
        "camera": "opencv",
        "x_position": 100,
        "y_position": 100,
    }

    def __init__(self, config_file: str):

        """
        Initialize Hermit configuration

        :param config_file: the path to the YAML configuration file
        """

        self.config_file = config_file
        self.shards_file = self.DefaultPaths["shards_file"]
        self.plugin_dir = self.DefaultPaths["plugin_dir"]
        self.config: Dict = {}
        self.commands: Dict = {}

        if path.exists(config_file):
            self.config = yaml.safe_load(open(config_file))

        if "shards_file" in self.config:
            self.shards_file = self.config["shards_file"]
        if "plugin_dir" in self.config:
            self.plugin_dir = self.config["plugin_dir"]
        if "commands" in self.config:
            self.commands = self.config["commands"]
        if "qr_system" in self.config:
            self.qr_system = self.config["qr_system"]
        else:
            self.qr_system = self.DefaultQRSystem

        defaults = self.DefaultCommands.copy()

        for key in defaults:
            if key not in self.commands:
                self.commands[key] = defaults[key]

        for key in self.commands:
            formatted_key = self.commands[key].format(self.shards_file)
            self.commands[key] = formatted_key


    @classmethod
    def load(cls):
        return HermitConfig(
            environ.get("HERMIT_CONFIG", cls.DefaultPaths["config_file"])
        )

_global_config = None

def get_config():
    global _global_config

    if _global_config is None:
        _global_config = HermitConfig.load()

    return _global_config
