Config
======

Hermit reads configuration data from a YAML configuration file at
startup.

The default location for this file is `/etc/hermit.yaml` (this path
can be changed by setting the `HERMIT_CONFIG` environment variable
before launching the `hermit` program).

An example configuration file is reproduced below from the
``examples`` directory of the `Hermit source code
<https://github.com/unchained-capital/hermit>`_:

.. literalinclude:: ../examples/config_files/hermit.example.yml
    :language: yaml

Default configuration is declared in the `HermitConfig` class.
Configuration from the YAML file (if present) is merged on top of the
default configuration and stored in a shared instance of the
`HermitConfig` class:

.. autoclass:: hermit.config.HermitConfig
