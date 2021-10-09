from yaml import safe_load
from os import environ
from os.path import exists
from typing import Optional

_global_config = None


def get_config() -> "HermitConfig":
    """Return a shared instance of :class:`HermitConfig`.

    This is the usual way to get configuration values in Hermit code.

    """
    global _global_config

    if _global_config is None:
        _global_config = HermitConfig.load()

    return _global_config


class HermitConfig:
    """Object to hold Hermit configuration

    Hermit configuration is split into three sections:

    * `paths` -- paths for configuration, shard data, and plugins, see :attr:`DefaultPaths`.
    * `commands` -- command-lines used to manipulate shard data, see :attr:`DefaultCommands`.
    * `io` -- settings for input and output, see :attr:`DefaultIO`.
    * `coordinator` -- settings for the coordinator, see :attr:`DefaultCoordinator`.

    This class is typically not instantiated directly.  Instead, the
    :func:`get_config` method is used to always return the same global
    configuration instance, e.g. ::

      >>> from hermit import get_config
      >>> print(get_config().paths["config_file"])
      "/etc/hermit.yml"

    """

    #: Default paths used by Hermit.
    #:
    #: The following paths are defined:
    #:
    #: * `config_file` -- path to the YAML file used for configuration
    #: * `shards_file` -- path to the BSON file used to store shards
    #: * `plugin_dir` -- path to a directory used to load runtime plugins
    DefaultPaths = {
        "config_file": "/etc/hermit.yaml",
        "shards_file": "/tmp/shard_words.bson",
        "plugin_dir": "/var/lib/hermit",
    }

    #: Default commands for persistence and backup of data.
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

    #: Default settings for input camera & output display.
    #:
    #: The following settings are defined:
    #:
    #: * `display` -- display mode (`opencv`, `framebuffer`, or `ascii`)
    #: * `camera` -- camera mode (`opencv` or `imageio`)
    #: * `qr_code_sequence_delay` -- time (in milliseconds) between each successive QR code in a sequence
    #: * `x_position` -- horizontal position of display on screen
    #: * `y_position` -- vertical position of display on screen
    #: * `height` -- width of display on screen
    #: * `width` -- height of display on screen
    #:
    DefaultIO = {
        "display": "opencv",
        "camera": "opencv",
        "qr_code_sequence_delay": 200,
        "x_position": 100,
        "y_position": 100,
        "width": 300,
        "height": 300,
    }

    #: Default settings for the coordinator being used with Hermit.
    #:
    #: * `signature_required` -- whether a signature from the
    #     coordinator is required to sign
    #:
    #: * `public_key` -- an RSA public key (in hex) corresponding to
    #     the private key used to sign by the coordinator
    #:
    DefaultCoordinator = {
        "signature_required": False,
        "public_key": None,
    }

    @classmethod
    def load(cls):
        """Return a properly initialized `HermitConfig` instance."""
        return HermitConfig(config_file=environ.get("HERMIT_CONFIG"))

    def __init__(self, config_file: Optional[str] = None):
        """Initialize Hermit configuration.

        :param config_file: the path to the YAML configuration file (defaults to `/etc/hermit.yml`).

        If the `config_file` does not exist, it will be ignored.

        """

        self._load(config_file=config_file)
        self._inject_defaults()
        self._interpolate_commands()
        self.paths = self.config["paths"]
        self.commands = self.config["commands"]
        self.io = self.config["io"]
        self.coordinator = self.config["coordinator"]

    def _load(self, config_file: Optional[str] = None) -> None:
        if config_file is None:
            config_file = self.DefaultPaths["config_file"]

        if exists(config_file):
            self.config = safe_load(open(config_file)) or {}
        else:
            self.config = {}

    def _inject_defaults(self) -> None:
        for section_key, defaults in [
            ("paths", self.DefaultPaths),
            ("commands", self.DefaultCommands),
            ("io", self.DefaultIO),
            ("coordinator", self.DefaultCoordinator),
        ]:
            if section_key not in self.config:
                self.config[section_key] = {}
            for config_key, default_value in defaults.items():
                if config_key not in self.config[section_key]:
                    self.config[section_key][config_key] = default_value

    def _interpolate_commands(self) -> None:
        for config_key in self.config["commands"]:
            interpolated_value = self.config["commands"][config_key].format(
                self.config["paths"]["shards_file"]
            )
            self.config["commands"][config_key] = interpolated_value
