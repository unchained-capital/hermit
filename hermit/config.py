import yaml
from os import path, environ
from typing import Dict


class HermitConfig:
    """Object to hold Hermit configuration

    Hermit reads its configuration from a YAML file on disk at
    `/etc/hermit.yaml` (by default).

    The following settings are supported:

    * `wallet_words_file` -- path to store wallet words
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
        'persistShards': "cat {0} | gzip -c - > {0}.persisted",
        'backupShards': "cp {0}.persisted {0}.backup",
        'restoreBackup': "zcat {0}.backup > {0}",
        'getPersistedShards': "zcat {0}.persisted > {0}"
    }

    DefaultPaths = {
        'config_file':  '/etc/hermit.yaml',
        'wallet_words_file': '/tmp/wallet_words.json',
        'shards_file': '/tmp/shard_words.bson',
        'plugin_dir': '/var/lib/hermit',
    }

    def __init__(self, config_file: str):

        """
        Initialize Hermit configuration

        :param config_file: the path to the YAML configuration file
        """

        self.config_file = config_file
        self.wallet_words_file = self.DefaultPaths['wallet_words_file']
        self.shards_file = self.DefaultPaths['shards_file']
        self.plugin_dir = self.DefaultPaths['plugin_dir']
        self.config: Dict = {}
        self.commands: Dict = {}
        
        if path.exists(config_file):
            self.config = yaml.safe_load(open(config_file))

        if 'wallet_words_file' in self.config:
            self.wallet_words_file = self.config['wallet_words_file']
        if 'shards_file' in self.config:
            self.shards_file = self.config['shards_file']
        if 'plugin_dir' in self.config:
            self.plugin_dir = self.config['plugin_dir']
        if 'commands' in self.config:
            self.commands = self.config['commands']

        defaults = self.DefaultCommands.copy()

        for key in defaults:
            if key not in self.commands:
                self.commands[key] = defaults[key]

        for key in self.commands:
            formatted_key = self.commands[key].format(self.wallet_words_file)
            self.commands[key] = formatted_key

    @classmethod
    def load(cls):
        return HermitConfig(environ.get("HERMIT_CONFIG", cls.DefaultPaths['config_file']))
