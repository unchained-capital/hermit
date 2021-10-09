Hermit
======
[![PyPI](https://img.shields.io/pypi/v/hermit.svg)](https://pypi.python.org/pypi)
[![Travis](https://img.shields.io/travis/unchained-capital/hermit.svg)](https://travis-ci.com/unchained-capital/hermit/)
[![Codecov](https://img.shields.io/codecov/c/github/unchained-capital/hermit.svg)](https://codecov.io/gh/unchained-capital/hermit/)

Hermit is a sharded,
[HD](https://en.bitcoin.it/wiki/Deterministic_wallet) command-line,
PSBT-compatible bitcoin wallet designed for indviduals and businesses
who demand the highest possible security.

Hermit is a dedicated **keystore**.  It is designed to operate in
tandem with a **coordinator**: an online wallet which can talk to a
blockchain.  The coordinator is responsible for generating all
transactions, transaction signature requests, and for receiving
transaction signatures from Hermit as well as constructing
fully-signed transactions and broadcasting them to the blockchain.

Hermit focuses on securely accepting signature requests from the
coordinator and generating signatures.

Coordinators currently compatible with Hermit:

* [Caravan](https://unchained-capital.github.io/caravan/#/)
* [Specter Desktop](https://specter.solutions/)
* [Sparrow](https://sparrowwallet.com/)
* [Fully Noded](https://fullynoded.app/)

Hermit's security features includes:

  * All communication between the user, Hermit, and the coordinator is
    done via QR codes, cameras, screen, and keyboard.  This means a
    Hermit installation does not require WiFi, Bluetooth, or any other
    form of wired or wireless communication. Hermit can operate in a
    completely air-gapped environment.

  * Private key data is sharded using SLIP-0039.  Each shard is
    encrypted with a separate password.  Hermit starts out in a
    "locked" state and multiple individuals can be made to be required
    to "unlock" a Hermit private key by employing multiple
    password-encrypted shards.

  * Hermit comes with a full management system for shards, allowing
    them to be re-encrypted, copied, deleted, and redealt.  This makes
    Hermit easier to use for organizations with turnover among their
    signing staff.

  * By default, Hermit uses the local filesystem for all storage of
    shard data.  This can be customized through configuration to use a
    TPM or other hardware secure element for shard storage.

  * Hermit will automatically lock itself after a short time of being
    unlocked with no user input.  Hermit can also be instantly locked
    in an emergency.

  * Signature requests from the coordinator can be signed with an RSA
    private key (held by the coordinator) and verified against the
    corresponding RSA public key (held in Hermit's configuration).
    This ensures that Hermit will only accept signature requests from
    a pre-configured coordinator.

  * Hermit is a command-line wallet but uses the operating systems'
    windowing system to display QR code animations and camera
    previews.  Hermit can be configured to instead operate using ASCII
    or with direct access to a framebuffer.  This allows installing
    Hermit on limited hardware without its own graphical system.

Hermit was designed for institutions who need to protect and use
bitcoin private keys.  Individuals holding bitcoin are probably better
served using hardware wallets and multisig.

Hermit is compatible with the following standards:

* [SLIP-0039](https://github.com/satoshilabs/slips/blob/master/slip-0039.md)
  standard for hierarchical Shamir sharding of private key data

* [PSBT](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)
  standard data format for bitcoin transactions

* [BCUR](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-005-ur.md)
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
shards> build-family-from-random              # create new shard family from random data
...
shards> list-shards                           # see newly created shards
...
shards> write                                 # save newly created shards to disk
shards> quit                                  # back to wallet mode
wallet> display-xpub m/45'/0'/0'              # display an extended public key
...
wallet> sign                                  # sign a bitcoin transaction
                                              # see tests/fixtures/signature_requests/2-of-2.p2sh.testnet.gif

...
```

See more details in the "Usage" section below.

Design
------

Hermit follows the following design principles:

  * Unidirectional information transfer -- information should only move in one direction
  * Always-on sharding & encryption -- keys should always be sharded and each shard encrypted
  * Open-source everything -- complete control over your software and hardware gives you the best security
  * Flexibility for human security -- you can customize Hermit's configuration & installation to suit your organization
  * Standards-compliant -- Hermit follows and sets best practices for high-security bitcoin wallets

### Sharding

Hermit is different than other wallets/keystores you may have used
(such as hardware wallets) because it always shards your key.

Sharding is done using
[SLIP-39](https://github.com/satoshilabs/slips/blob/master/slip-0039.md)
which means there are two levels of structure:

* Groups -- some quorum of *P* of *Q* groups is required to unlock a key

* Shards -- some quorum of *n* of *m* shards is required to unlock
  each group, with *n* and *m* possibly different for each group

This structure creates a lot of flexibility for different scenarios.

Hermit extends the current SLIP-39 proposal by encrypting each shard
with a password.

Each shard has its own password, allowing for teams to operate a key
together, each team member operating a given shard (in some
group). However, if the user explicitly supplies an empty string as
the password when either creating a shard, or changing the password on
the shard, the resulting shard will be unencrypted. While this makes
the transport of the shard less safe, it does make it possible to
export the shards to technologies that support only unencrypted
SLIP-39 implementations.

#### Compatibility with other wallets

If you are using a non-sharded wallet such as a hardware wallet
(Trezor, Ledger, Coldcard, Electrum, &c.), you can import your key
from your BIP39 "seed phrase" and Hermit will shard it for you.

You may also input a new key using whatever source of randomness you
like.

Hermit will **not** export keys as BIP39 phrases; only as encrypted
SLIP39 phrases.  This means it is challenging to extract a key from a
Hermit installation for use in, for example, a hardware wallet or
Electrum.  This constraint is present by design.

### Input & Output

Hermit is designed to be deployed in air-gapped environments.

* The only way data should be able to enter the device Hermit is
  running on is via keyboard and camera.

* The only way data can leave Hermit is via the screen of the device
  it is running on.

Hermit has no idea what is happening on the blockchain and relies on
an external, online wallet application to draft transaction requests.
These transaction requests are passed to Hermit via QR codes.
Signatures produced by Hermit are similarly displayed on screen as QR
codes.

The usage of QR codes for transaction requests and signatures creates
a limit to how complex of a transaction Hermit can sign.  This
limitation will be addressed by a QR code packeting algorithm one day.

### Storage

Hermit uses 3 storage locations:

     _________               _____________                  ____________
    |         |             |             |                |            |
    | memory  | -- write -> | filesystem  | -- persist --> | data store |
    |_________|             |_____________|                |____________|


When Hermit first boots, shards from the data store or filesystem
(in that order) are loaded into memory.  Changes made to shards
are always made *in memory* and will not survive Hermit restarts.

To save data across Hermit restarts, ensure you `write` it to the
filesystem.

If your Hermit lives on a read-only filesystem, to save data
across Hermit machine restarts, ensure you `persist` it to the
data store.

### Modes

Hermit is a modal application with two modes:

* `wallet` mode is where you will spend most of your time, signing transactions and exporting public keys
* `shards` mode is accessed when you need to import keys or shards, export shards, or otherwise change something about how your key is unlocked

### Data Format

Hermit uses animated QR codes for input/output of arbitrary sized data
(mostly PSBTs).  Data is split up and resassembled using the
[BCUR](https://github.com/BlockchainCommons/Research/blob/master/papers/bcr-2020-005-ur.md)
standard.

Usage
-----

### Installation

Installing Hermit can be done via `pip3`:

```
$ pip3 install hermit
```

If you want to develop against Hermit, see the "Developers" section
below for a different way of installing Hermit.

### Starting Hermit

To start Hermit, just run the `hermit` command.

```
$ hermit
```

You can also pass a configuration file

```
$ HERMIT_CONFIG=/path/to/hermit.yml hermit
```

See the "Configuration" section below for more information on how to
configure Hermit.

### Creating a Key

Before you can do much with Hermit you'll need to create or import at
least one key.  To do so, first enter shards mode:

```
$ hermit
...
wallet> shards
```

Two `shard` mode commands will let you import a key:

* `build-family-from-phrase` -- enter a BIP39 phrase.  This is useful if you are importing a key from a hardware wallet such as Trezor, Ledger, Coldcard or from another software wallet such as Electrum.
* `build-family-from-random` -- enter random characters.   This is useful if you want to generate your own entropy (from, say, rolling dice)

Whichever you choose, you will be prompted to enter a shard
configuration.

Creating a secure shard set from a key requires additional randomness
beyond the seed of the key.  So even if you choose to
`build-family-from-phrase`, you will still be asked to input random
characters.  Ensure you are prepared to do so using a good source of
randomness (such as rolling dice).


### Displaying Wallet Data

Hermit can export public keys (or extended public keys) from the key
it protects.  These are useful for other applications which want to
refer to Hermit's key but, obviously, can't be allowed to see its
private contents.

Two `wallet` mode commands are useful for this:

* `display-xpub` -- exports an extended public key
* `display-pub` -- exports a  public key

Each of these commands expects a BIP32 path as an argument and each
will display its data as a QR code.

### Signing Transactions

The whole point of Hermit is to ultimately sign transactions.
Transaction signature requests must be created by an external
application (but see the example requests in
[tests/fixtures/signature_requests](tests/fixtures/signature_requests)).

Once you have a signature request, and you're in `wallet` mode, you
can run `sign` to start signing a Bitcoin transaction.

### Configuration

Hermit looks for a configuration file at `/etc/hermit.yml` by default.
You can change this path by passing the`HERMIT_CONFIG` environment
variable when you start the `hermit` program:

```
$ HERMIT_CONFIG=/path/to/hermit.yml hermit
```

The configuration file is a YAML file.  See the documentation for the
`HermitConfig` class for details on allowed configuration settings.


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
