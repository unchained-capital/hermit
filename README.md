Hermit
======
[![PyPI](https://img.shields.io/pypi/v/hermit.svg)](https://pypi.python.org/pypi)
[![Travis](https://img.shields.io/travis/unchained-capital/hermit.svg)](https://travis-ci.com/unchained-capital/hermit/)
[![Codecov](https://img.shields.io/codecov/c/github/unchained-capital/hermit.svg)](https://codecov.io/gh/unchained-capital/hermit/)

Hermit is a **keystore** designed for operating bitcoin businesses
that demand the highest possible security for private keys.

Hermit is designed to operate in tandem with a **coordinator**: an
online wallet which can talk to a blockchain.  The coordinator is
responsible for generating all transactions, transaction signature
requests, and for receiving transaction signatures from Hermit as well
as constructing fully-signed transactions and broadcasting them to the
blockchain.

Hermit is compatible with the following coordinator software:

* [Caravan](https://unchained-capital.github.io/caravan/#/)
* [Specter Desktop](https://specter.solutions/)
* [Sparrow](https://sparrowwallet.com/)
* [Fully Noded](https://fullynoded.app/)
  
Hermit focuses on securely storing a sharded private key, validating
signature requests from the coordinator, and generating transaction
signatures.

Hermit is compatible with the following standards:

* [SLIP-0039](https://github.com/satoshilabs/slips/blob/master/slip-0039.md)
  standard for hierarchical Shamir sharding of private key data

* [BIP-0032](https://en.bitcoin.it/wiki/BIP_0032) standard for
  hierarchical deterministic (HD) wallets

* [PSBT](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)
  standard data format for bitcoin transactions

* [BC-UR](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-005-ur.md)
  standard for transporting data through QR code URIs
  
Quickstart
----------

```
$ pip3 install hermit                         # may need 'sudo' for this command
...
$ hermit                                      # launch hermit
...
wallet> help                                  # see wallet commands
...
wallet> shards                                # enter shard mode
...
shards> help                                  # see shard commands
...
shards> list-shards                           # see current shards
...
shards> build-family-from-phrase              # create new shard family from BIP39 phrase

merge alley lucky axis penalty manage
latin gasp virus captain wheel deal
chase fragile chapter boss zero dirt
stadium tooth physical valve kid plunge

[CTRL-D]

....

shards> list-shards                           # see newly created shards
...
shards> write                                 # save newly created shards to disk
shards> quit                                  # back to wallet mode
wallet> display-xpub m/45'/0'/0'              # display an extended public key
...
wallet> sign                                  # sign a bitcoin transaction

# See tests/fixtures/signature_requests/2-of-2.p2sh.testnet.gif

...
```

See more details in the "Usage" section below.

Design
------

Hermit follows the following design principles:

  * Unidirectional information transfer -- information should only move in one direction
  * Always-on sharding & encryption -- private keys should always be sharded and each shard encrypted
  * Open-source everything -- complete control over your software and hardware gives you the best security
  * Flexibility for human security -- you can customize Hermit's configuration & installation to suit your organization
  * Standards-compliant -- Hermit follows and sets best practices for high-security bitcoin wallets

Hermit's features include:

  * All communication between the user, Hermit, and the coordinator is
    done via QR codes, cameras, screen, and keyboard.  This means a
    Hermit installation does not require WiFi, Bluetooth, or any other
    form of wired or wireless communication. Hermit can operate in a
    completely air-gapped environment.

  * Private key data is sharded using
    [SLIP-0039](https://github.com/satoshilabs/slips/blob/master/slip-0039.md).
    Each shard is encrypted with a separate password.  Hermit starts
    out in a "locked" state and multiple individuals can be made to be
    required to "unlock" a Hermit private key by employing multiple
    password-encrypted shards.

  * Hermit will automatically lock itself after a short time of being
    unlocked with no user input.  Hermit can also be instantly locked
    in an emergency.
	
  * Hermit comes with a full management system for shards, allowing
    them to be re-encrypted, copied, deleted, and redealt.  This makes
    Hermit easier to use for organizations with turnover among their
    signing staff.

  * By default, Hermit uses the local filesystem for all storage of
    shard data.  This can be customized through configuration to use a
    TPM or other hardware secure element for shard storage.

  * Signature requests from the coordinator can be signed with an
    ECDSA private key (held by the coordinator) and verified against
    the corresponding public key (held in Hermit's configuration).
    This ensures that Hermit will only accept signature requests from
    a pre-authenticated coordinator.

  * Hermit is a command-line wallet but uses the operating systems'
    windowing system to display QR code animations and camera
    previews.  Hermit can be configured to instead operate using ASCII
    or with direct access to a framebuffer.  This allows installing
    Hermit on limited hardware without its own graphical system.


Usage
------

Installing Hermit can be done via `pip3`:

```
$ pip3 install hermit
```

If you want to develop against Hermit, see the "Developers" section
below for a different way of installing Hermit.

To start Hermit, just run the `hermit` command.

```
$ hermit
```

This is enough to get started playing with Hermit.  For production
usage, you'll want to configure Hermit through its configuration file.

By default, Hermit looks for a configuration file at
`/etc/hermit.yml`, but you can change this by passing in a different
configuration file path through an environment variable when you
launch `hermit`:

```
$ HERMIT_CONFIG=/path/to/hermit.yml hermit
```

See the documentation for the `HermitConfig` class for details on
allowed configuration settings.

### Signing Transactions

The ultimate point of Hermit is to securely sign bitcoin transactions.

Assuming Hermit has a private key, you can run the following commands
to unlock it and sign a bitcoin transaction:

```
wallet> unlock
...
wallet> sign

# Scan transaction signature request...
```

If you don't unlock the private key first, Hermit will preview the
transaction signature request for you and abort signing.

Remember: Hermit does not create transactions.  An external
coordinator application must pass Hermit an unsigned
[PSBT](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)
which Hermit interprets as a transaction signature request (you can
find examples of such requests in
[tests/fixtures/signature_requests](tests/fixtures/signature_requests)).


### Exporting Extended Public Keys (xpubs)

Hermit can export extended public keys (xpubs) derived from a private
key.

```
wallet> unlock
wallet> display-xpub m/45'/0'/0'
xpub...
```

Extended public keys are printed to screen and displayed as QR codes.

### Private Key Management

Hermit stores all private keys in a sharded format.

Sharding is done using
[SLIP-0039](https://github.com/satoshilabs/slips/blob/master/slip-0039.md)
which means there are two levels of structure:

* Groups -- some quorum *P* of *Q* groups is required to unlock a key

* Shards -- some quorum *m* of *n* shards is required to unlock
  each group, with *m* and *n* possibly different for each group

This structure creates a lot of flexibility for different scenarios.
For example:

* With *P=Q=1* and *n=m=1*, SLIP-0039 only a single shard is used.
  This is useful for testing but not the expected usage pattern.

* With *P=Q=1*, SLIP-0039 reproduces *m* of *n* Shamir sharding with
  *n* shards, *m* of which are required to unlock the private key.

* *P=Q=2*; one group is 3 of 5, the other is 1 of 3.  This allows one
  group of 5 "reviewers" of which at least 3 are required and another
  group of 3 "admins", only 1 of which is required.

Hermit extends the current SLIP-39 proposal by encrypting each shard
with a password.

Each shard has its own password, allowing for teams to operate a key
together, each team member operating a given shard (in some
group).

However, if the user explicitly supplies an empty string as the
password when creating a shard (or changing the password on the
shard), the resulting shard will be unencrypted.  While this makes the
storage of the shard less secure, it does make it possible to export
the shards to technologies that support only unencrypted SLIP-39
implementations (e.g. Trezor).

#### Creating a private key

A new private key can be created by entering random data through the
keyboard:

```
wallet> shards
shards> build-family-from-random
```

Random data should be generated using a trusted source of randomness.
Analog randomness such as from fair dice is relatively fast to enter
through this method.

#### Importing a private key

If you are using a non-sharded wallet such as a hardware wallet
(Trezor, Ledger, Coldcard, Electrum, &c.), you can import your private
key from your
[BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
"seed phrase" and Hermit will shard it for you.

```
wallet> shards
shards> build-family-from-phrase
```

A sharded private key requires more randomness than an unsharded
private key so Hermit will require you enter random data to create the
shards.

**Note:** Hermit will **not** export keys as BIP39 phrases; only as
encrypted SLIP39 phrases.  This means it is challenging to extract a
key from a Hermit installation for use in, for example, a hardware
wallet or Electrum.  This constraint is present by design.


#### Resharding a private key

A private key already stored in Hermit can be resharded into a
different configuration of groups and/or shards.

```
wallet> shards
shards> build-family-from-family
```

Building new shards for an existing private key requires new
randomness so Hermit will require you enter random data to create the
shards.

#### Importing & exporting shards

Shards can be individually imported & exported, which allows moving
entire sharded private keys between Hermit installations.

Importing & exporting can be done through QR codes or through
encrypted SLIP-0039 phrases.

For example, at the source Hermit installation:

```
wallet> shards
shards> export-shard-as-phrase shard1

Encrypted SLIP39 phrase for shard random:

friar merchant academic academic analysis ...

shards> export-shard-as-qr shard2
```

and at the destination Hermit installation:

```
wallet> shards
shards> import-shard-from-phrase shard1

Enter SLIP39 phrase for shard foo below (CTRL-D to submit):

friar merchant academic academic analysis ...

shards> import-shard-from-qr shard2

```

#### Copying & deleting shards

Shards can also be copied and deleted.  This allows transferring a
shard from one operator to another.

```
wallet> shards
shards> copy-shard shard1 shard1_new
old password> ********
new password> **********
confirm> **********
shards> delete-shard random2
Really delete shard random2? yes
```

#### Shard Storage

Hermit uses 3 storage locations for shard data:

     _________               _____________                  ____________
    |         |             |             |                |            |
    | memory  | -- write -> | filesystem  | -- persist --> | data store |
    |_________|             |_____________|                |____________|
    

When Hermit first boots, shards from the data store or filesystem
(in that order) are loaded into memory.  Changes made to shards
are always made *in memory* and will not survive Hermit restarts.

This is because Hermit never writes to the filesystem unless asked. To
save data across Hermit restarts, the `write` command must be run
(while in `shards` mode).

This will cause shard data in memory to be written to the file
`/tmp/shard_words.bson`.  This path **should be changed** to an
appropriate value through the following configuration file setting:

```
# in /etc/hermit.yml
shards_file: /home/user/shard_words.bson
```

Hermit may be running on a read-only filesystem.  In this case, the
`persist` command can be used to execute custom code to persist data
from the filesystem to a more durable location (e.g. - custom
hardware).

See the documentation for `HermitConfig.DefaultCommands` for more
details on shard persistence.

Developers
----------

Developers will want to clone a copy of the Hermit source code:

```
$ git clone https://github.com/unchained-capital/hermit
$ cd hermit
$ make
```

**NOTE:** To develop using the Hermit code in this directory, run
`source environment.sh`.  This applies to all the commands below in
this section.

Hermit ships with a full test suite
([pytest](https://docs.pytest.org/en/latest/)).  Run it as follows:

```
$ make test
```

The code can also be run through a linter
([black](https://black.readthedocs.io/en/stable/)) & type-checker
([mypy](http://mypy-lang.org/)).

```
$ make lint
```

Hermit has been tested on the following platforms:

* macOS Big Sur 11.3
* Linux Ubuntu 18.04
* Linux Slax 9.6.4

### Contributing to Hermit

Unchained Capital welcomes bug reports, new features, and better
documentation for Hermit.  To contribute, create a pull request (PR)
on GitHub against the [Unchained Capital fork of
Hermit](https://github.com/unchained-capital/hermit).

Before you submit your PR, make sure to lint your code and run the test suite!

```
$ source environment.sh
$ make test
$ make lint
```
