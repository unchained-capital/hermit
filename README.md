Hermit
======
[![PyPI](https://img.shields.io/pypi/v/hermit.svg)](https://pypi.python.org/pypi)
[![Travis](https://img.shields.io/travis/unchained-capital/hermit.svg)](https://travis-ci.com/unchained-capital/hermit/)
[![Codecov](https://img.shields.io/codecov/c/github/unchained-capital/hermit.svg)](https://codecov.io/gh/unchained-capital/hermit/)

Hermit is not like most bitcoin wallets.  Hermit doesn't connect to
the Internet and it doesn't know about the state of the bitcoin
blockchain.

Hermit is a **keystore**: an application that stores private keys and
uses them to sign bitcoin transactions.  Hermit focuses on:

* storing private keys on high-security, airgapped hardware

* validating unsigned bitcoin transactions across the airgap

* returning signed bitcoin transactions across the airgap

Hermit is designed to operate in tandem with a **coordinator**: an
Internet-connected application which does understand the state of the
bitcoin blockchain.  The coordinator is responsible for

* generating unsigned (or partially signed) transactions to pass to
  Hermit

* receiving signed transactions from Hermit

* constructing fully-signed transactions and broadcasting them to the
  bitcoin blockchain

This separation of concerns between keystores and coordinators allows
Hermit to be used by operating businesses that demand the highest
possible security for private keys.

Hermit is compatible with the following standards:

* [SLIP-0039](https://github.com/satoshilabs/slips/blob/master/slip-0039.md)
  standard for hierarchical Shamir sharding of private key data

* [BIP-0032](https://en.bitcoin.it/wiki/BIP_0032) standard for
  hierarchical deterministic (HD) wallets

* [PSBT](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)
  standard data format for bitcoin transactions

* [BC-UR](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-005-ur.md)
  standard for transporting data through QR code URIs

Hermit is compatible with the following coordinator software:

* [Unchained Capital](https://unchained.com)
* [Caravan](https://unchained-capital.github.io/caravan/#/)
<!-- * [Specter Desktop](https://specter.solutions/) -->
<!-- * [Sparrow](https://sparrowwallet.com/) -->
<!-- * [Fully Noded](https://fullynoded.app/) -->

Features
--------

  * **Air-Gapped:** All communication between the user, Hermit, and
    the coordinator is done via QR codes, cameras, screen, and
    keyboard.  This means a Hermit installation does not require WiFi,
    Bluetooth, or any other form of wired or wireless
    communication. Hermit can operate in a completely air-gapped
    environment.

  * **Supports Signing Teams:** Private key data is (hierarchically)
    sharded into P-of-Q groups with each group requiring m-of-n shards
    (with m & n possibly differing among the Q groups).  Shards can be
    copied, deleted, and re-created.  This makes it possible to
    operate Hermit using a team of signers with no individual having
    unilateral access to the private key.  Turnover on signing teams
    can be accommodated by rotating shards.

  * **Encrypted:** Private key shards are encrypted and must be
    decrypted using shard-specific passwords before they can be
    combined.

  * **Requires Unlocking**: The combination of encryption and sharding
    means that Hermit's private keys must be "unlocked" before it can
    be used.  Unlocking requires shard-specific passwords to m-of-n
    shards for P-of-Q groups.  Hermit will automatically lock itself
    after a short time of being unlocked with no user input.  Hermit
    can also be instantly locked in an emergency.

  * **Can Use Security Modules:** By default, Hermit uses the local
    filesystem for all storage of shard data.  This can be customized
    through configuration to use a trusted platform module (TPM) or
    hardware security module (HSM) for shard storage.

  * **Runs on Low-End Hardware:** Hermit is a command-line application
    but uses the operating system's windowing system to display QR
    code animations and camera previews.  Hermit can be configured to
    instead operate using ASCII or with direct access to a
    framebuffer.  This allows installing Hermit on limited hardware
    without a graphical system (e.g. terminal only).

  * **Coordinator Authorization:** Transactions received from a
    coordinator can be signed with an ECDSA private key (held by the
    coordinator) and verified against the corresponding public key
    (held in Hermit's configuration).  This ensures that Hermit will
    sign transactions from an authorized coordinator.

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

Usage
------

## Installation

Installing Hermit can be done via `pip3`:

```
$ pip3 install hermit
```

If you want to develop against Hermit, see the "Developers" section
below for a different way of installing Hermit.

## Startup

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

## Private Key Management

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

     _________               _____________                  _________
    |         |             |             |                |         |
    | memory  | -- write -> | filesystem  | -- persist --> | TPM/HSM |
    |_________|             |_____________|                |_________|
    

Hermit does not assume that the filesystem it is running from is
writeable and so never writes to the filesystem *unless asked*.  New
shards or changes made to existing shards are therefore always made
*in memory only* and will not survive Hermit restarts.

To save shard data across Hermit restarts, the `write` command must be
run (while in `shards` mode).

This will cause shard data in memory to be written to the file
`/tmp/shard_words.bson`.  This path **should be changed** to an
appropriate value through the following configuration file setting:

```
# in /etc/hermit.yml
shards_file: /home/user/shard_words.bson
```

If Hermit is running on a device with a TPM or HSM then shards can be
directly stored in the TPM/HSM.  The `persist` command can be run
(while in `shards` mode) to execute shell commands to persist data
from the filesystem to a more durable location (e.g. - custom
hardware).

When Hermit first boots, shards from the TPM/HSM or filesystem (in
that order) are loaded into memory.

See the documentation for `HermitConfig.DefaultCommands` for more
details on shard persistence.

## Signing Transactions

Assuming Hermit has a private key, you can run the following commands
to unlock it and sign a bitcoin transaction:

```
wallet> unlock
...
wallet> sign

# Scan unsigned transaction...
```

If you don't unlock the private key first, Hermit will preview the
transaction for you and abort signing.

Remember: Hermit does not create transactions.  An external
coordinator application must pass Hermit an unsigned
[PSBT](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)
which Hermit interprets.

You can find examples of such requests in
[tests/fixtures/signature_requests](tests/fixtures/signature_requests).

## Exporting Extended Public Keys (xpubs)

Hermit can export extended public keys (xpubs) derived from a private
key.

```
wallet> unlock
wallet> display-xpub m/45'/0'/0'
xpub...
```

Extended public keys are printed to screen and displayed as QR codes.

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

The code can also be run through linters (
([black](https://black.readthedocs.io/en/stable/) &
[flake8](https://flake8.pycqa.org/en/latest/)) and a type-checker
([mypy](http://mypy-lang.org/)).

```
$ make check
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

Before you submit your PR, make sure to check your code and run the
test suite!

```
$ source environment.sh
$ make check test
```
