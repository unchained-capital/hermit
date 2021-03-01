from unittest.mock import patch

import hermit
from hermit.config import HermitConfig


class TestHermitPaths(object):

    defaults = {
        "persistShards": "cat {0} | gzip -c - > {0}.persisted",
        "backupShards": "cp {0}.persisted {0}.backup",
        "restoreBackup": "zcat {0}.backup > {0}",
        "getPersistedShards": "zcat {0}.persisted > {0}",
    }

    #
    # Loading
    #

    @patch("hermit.config.path.exists")
    def test_with_no_config_file(self, mock_exists):
        mock_exists.return_value = False
        config = HermitConfig.load()
        assert (
            config.config_file == hermit.config.HermitConfig.DefaultPaths["config_file"]
        )
        assert (
            config.shards_file == hermit.config.HermitConfig.DefaultPaths["shards_file"]
        )
        assert (
            config.plugin_dir == hermit.config.HermitConfig.DefaultPaths["plugin_dir"]
        )

    @patch("hermit.config.environ.get")
    def test_with_config_file(self, mock_environ_get):
        mock_environ_get.return_value = "./tests/fixtures/hermit.yaml"
        config = HermitConfig.load()
        assert config.shards_file == "test.bson"
        assert config.plugin_dir == "testdir"

    #
    # Paths
    #

    @patch("hermit.config.path.exists")
    @patch("hermit.config.yaml.safe_load")
    @patch("hermit.config.open")
    def test_paths_can_be_set(self, mock_open, mock_safe_load, mock_exists):
        shards_file = "shards_file"
        plugin_dir = "plugin_dir"
        mock_exists.return_value = True
        mock_safe_load.return_value = {
            "shards_file": shards_file,
            "plugin_dir": plugin_dir,
        }
        config = hermit.config.HermitConfig.load()
        assert config.shards_file == shards_file
        assert config.plugin_dir == plugin_dir

    #
    # Commands
    #

    @patch("hermit.config.path.exists")
    @patch("hermit.config.yaml.safe_load")
    @patch("hermit.config.open")
    def test_can_set_command(self, mock_open, mock_safe_load, mock_exists):
        mock_exists.return_value = True
        mock_safe_load.return_value = {"commands": {"persistShards": "foo {0}"}}
        config = HermitConfig.load()
        assert config.commands["persistShards"] == "foo {}".format(config.shards_file)
