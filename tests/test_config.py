from yaml import dump
from io import BytesIO
from unittest.mock import patch, Mock

import hermit
from hermit import get_config
from hermit.config import HermitConfig

class TestHermitConfig(object):

    InterpolatedDefaultCommands = {
        "persistShards": "cat /tmp/shard_words.bson | gzip -c - > /tmp/shard_words.bson.persisted",
        "backupShards": "cp /tmp/shard_words.bson.persisted /tmp/shard_words.bson.backup",
        "restoreBackup": "zcat /tmp/shard_words.bson.backup > /tmp/shard_words.bson",
        "getPersistedShards": "zcat /tmp/shard_words.bson.persisted > /tmp/shard_words.bson",
    }

    #
    # HemitConfig.load
    #

    @patch("hermit.config.HermitConfig")
    @patch("hermit.config.environ.get")
    def test_load_with_no_environment_variable(self, mock_environ_get, mock_HermitConfig):
        mock_environ_get.return_value = None
        mock_config = Mock()
        mock_HermitConfig.return_value = mock_config
        assert HermitConfig.load() == mock_config
        mock_environ_get.assert_called_once_with("HERMIT_CONFIG")
        mock_HermitConfig.assert_called_once_with(config_file=None)


    @patch("hermit.config.HermitConfig")
    @patch("hermit.config.environ.get")
    def test_load_with_environment_variable(self, mock_environ_get, mock_HermitConfig):
        mock_environ_get.return_value = "/tmp/hermit.yml"
        mock_config = Mock()
        mock_HermitConfig.return_value = mock_config
        assert HermitConfig.load() == mock_config
        mock_environ_get.assert_called_once_with("HERMIT_CONFIG")
        mock_HermitConfig.assert_called_once_with(config_file="/tmp/hermit.yml")

    #
    # HemitConfig.__init__
    #

    @patch("hermit.config.exists")
    def test_init_with_no_config_file(self, mock_exists):
        mock_exists.return_value = False
        config = HermitConfig()
        assert config.paths == HermitConfig.DefaultPaths
        assert config.commands == self.InterpolatedDefaultCommands
        assert config.io == HermitConfig.DefaultIO
        mock_exists.assert_called_once_with(HermitConfig.DefaultPaths["config_file"])

    @patch("hermit.config.exists")
    def test_init_with_non_existent_config_file(self, mock_exists):
        mock_exists.return_value = False
        config = HermitConfig(config_file="/tmp/hermit.yml")
        assert config.paths == HermitConfig.DefaultPaths
        assert config.commands == self.InterpolatedDefaultCommands
        assert config.io == HermitConfig.DefaultIO
        mock_exists.assert_called_once_with("/tmp/hermit.yml")

    @patch("hermit.config.exists")
    @patch("hermit.config.open")
    def test_init_with_existing_but_zero_byte_config_file(self, mock_open, mock_exists):
        mock_exists.return_value = True
        mock_open.return_value = BytesIO(b'')
        config = HermitConfig(config_file="/tmp/hermit.yml")
        assert config.paths == HermitConfig.DefaultPaths
        assert config.commands == self.InterpolatedDefaultCommands
        assert config.io == HermitConfig.DefaultIO
        mock_exists.assert_called_once_with("/tmp/hermit.yml")

    @patch("hermit.config.exists")
    @patch("hermit.config.open")
    def test_init_with_existing_but_empty_config_file(self, mock_open, mock_exists):
        config = dict()
        mock_exists.return_value = True
        mock_open.return_value = BytesIO(bytes(dump(config), "utf8"))
        config = HermitConfig(config_file="/tmp/hermit.yml")
        assert config.paths == HermitConfig.DefaultPaths
        assert config.commands == self.InterpolatedDefaultCommands
        assert config.io == HermitConfig.DefaultIO
        mock_exists.assert_called_once_with("/tmp/hermit.yml")

    @patch("hermit.config.exists")
    @patch("hermit.config.open")
    def test_init_with_existing_but_empty_config_file(self, mock_open, mock_exists):
        config = dict()
        mock_exists.return_value = True
        mock_open.return_value = BytesIO(bytes(dump(config), "utf8"))
        config = HermitConfig(config_file="/tmp/hermit.yml")
        assert config.paths == HermitConfig.DefaultPaths
        assert config.commands == self.InterpolatedDefaultCommands
        assert config.io == HermitConfig.DefaultIO
        mock_exists.assert_called_once_with("/tmp/hermit.yml")


    @patch("hermit.config.exists")
    @patch("hermit.config.open")
    def test_init_with_complex_config_file(self, mock_open, mock_exists):
        config = dict(
            paths=dict(
                shards_file="/root/shards.bson",
            ),
            commands=dict(
                persistShards="cat {0} | something_else | gzip -c - > {0}.persisted",
            ),
            io=dict(
                x_position=200,
                y_position=200,
            ),
        )
        mock_exists.return_value = True
        mock_open.return_value = BytesIO(bytes(dump(config), "utf8"))
        config = HermitConfig(config_file="/tmp/hermit.yml")

        assert config.paths["shards_file"] == "/root/shards.bson"
        assert config.paths["config_file"] == HermitConfig.DefaultPaths["config_file"]
        assert config.paths["plugin_dir"] == HermitConfig.DefaultPaths["plugin_dir"]

        assert config.commands["persistShards"] == "cat /root/shards.bson | something_else | gzip -c - > /root/shards.bson.persisted"
        assert config.commands["backupShards"] == "cp /root/shards.bson.persisted /root/shards.bson.backup"
        assert config.commands["restoreBackup"] == "zcat /root/shards.bson.backup > /root/shards.bson"
        assert config.commands["getPersistedShards"] == "zcat /root/shards.bson.persisted > /root/shards.bson"

        assert config.io["display"] == HermitConfig.DefaultIO["display"]
        assert config.io["camera"] == HermitConfig.DefaultIO["camera"]
        assert config.io["x_position"] == 200
        assert config.io["y_position"] == 200
        assert config.io["width"] == 300
        assert config.io["height"] == 300
        assert config.io["qr_code_sequence_delay"] == 200

        mock_exists.assert_called_once_with("/tmp/hermit.yml")

def test_get_config():
    get_config().paths["test_path"] = "foobar"
    assert get_config().paths["test_path"]== "foobar"
