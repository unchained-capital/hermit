Hermit
======

Hermit is a sharded,
[HD](https://en.bitcoin.it/wiki/Deterministic_wallet) command-line
signing tool designed for cryptocurrency owners who demand the highest
possible form of security.

Hermit operates in tandem with an online wallet which can talk to the
blockchain.  All communication between the user, Hermit, and the
online wallet is done via QR codes, cameras, screen, and keyboard.

A Hermit installation does not require WiFi, Bluetooth, or any other
form of wired or wireless communication.  Hermit is instead designed
to be run on modified commercial or open-source hardware running a
custom, barebones operating system, a so-called "air-gapped"
deployment.

Quickstart
----------

Video: TBD

```
$ pip install hermit                          # may need 'sudo' for this command
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
wallet> export-xpub m/45'/0'/0'               # export an extended public key
...
wallet> sign-bitcoin                          # sign a bitcoin transaction
                                              # see examples/signature_requests/bitcoin_testnet.jpg

...
```

See more details in the "Usage" section below.

Design
------

Hermit follows the following design principles:

  * Unidirectional information transfer -- information should only move in one direction
  * Always-on sharding & encryption -- keys should always be sharded and each shard encrypted
  * Open-source everything -- complete control over your software and hardware gives you the best security
  * Flexibility for human security -- you can customize the sharding configuration to suit your organization

### Audience
  
Hermit is a difficult to use but highly-secure wallet.  

Hermit is **not recommended** for non-technical individuals with a
small amount of cryptocurrency.

Hermit is designed for computer-savvy people and organizations to
self-custody significant sums.

### Sharding

Hermit is different than other wallets you may have used because it
always shards your key.

Sharding is done using
[SLIP-39](https://github.com/satoshilabs/slips/blob/master/slip-0039.md)
which means there are two levels of structure:

* Groups -- some quorum of *N* of *M* groups is required to unlock a key

* Shards -- some quorum of *N_G* of *M_G* shards is required to unlock
  a group *G*, with *N_G* and *M_G* possibly different for each group

This structure creates a lot of flexibility for different scenarios.

Shards in Hermit are always encrypted by a password.  Each shard has
its own password, allowing for teams to operate a key together, each
team member operating a given shard (in some group).

#### Compatibility with other wallets

If you are using a non-sharded wallet such as a hardware wallet
(Trezor, Ledger, &c.) or Electrum, you can import your key from your
BIP39 "seed phrase" and Hermit will shard it for you.

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

### Bitcoin Only

As a sharded, HD wallet, Hermit is a tool that can be used with any
cryptocurrency that operates with the BIP32 standard.

But Hermit also ships with a `sign-bitcoin` command that will sign
Bitcoin (BTC) transactions.

You can extend Hermit for other cryptocurrencies if you need; see the
"Plugins" section below.

Usage
-----

### Installation

Installing Hermit can be done via `pip`:

```
$ pip install hermit
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
leaest one key.  To do so, first enter shards mode:

```
$ hermit
...
wallet> shards
```

Two `shard` mode commands will let you import a key:

* `build-family-from-phrase` -- enter a BIP39 phrase.  This is useful if you are important a key from a hardware wallet such as Trezor or Ledger or from another software wallet such as Electrum.
* `build-family-from-random` -- enter random characters.   This is useful if you want to generate your own entropy (from, say, rolling dice)

Whichever you choose, you will be prompted to enter a shard configuration.

Creating a secure shard set from a key requires additional randomness
beyond the seed of the key.  So even if you choose to
`build-family-from-phrase`, you will still be asked to input random
characters.  Ensure you are prepared to do so using a good source of
randomness (such as rolling dice).

####  Advanced Sharding Operations

Once you have a key in a particular shard configuration, you can do
some interesting things (ensure you are already in `shards` mode):

##### Rotate out a signer

TBD

##### Export shards

TBD

### Exporting Public Keys

Hermit can export public keys (or extended public keys) from the key
it protects.  These are useful for other applications which want to
refer to Hermit's key but, obviously, can't be allowed to see its
private contents.

Two `wallet` mode commands are useful for this:

* `export-xpub` -- exports an extended public key
* `export-pub` -- exports a  public key

Each of these commands expects a BIP32 path as an argument and each
will display its data as a QR code.

### Signing Transactions

The whole point of Hermit is to ultimately sign transactions.
Transaction signature requests must be created by an external
application.  You can also use a test signature request available at
[examples/signatur_requests/bitcoin.jpg](examples/signatur_requests/bitcoin.jpg).

Once you have a signature request, and you're in `wallet` mode, you
can run `sign-bitcoin` to start signing a Bitcoin transaction.

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

### Testing

Hermit ships with a full [pytest] suite.  Run it as follows:

```
$ source environment.sh
$ make test
$ make lint
```

Hermit has been tested on the following platforms:

* OS X High Sierra 10.13.6
* Linux Ubuntu 18.04
* Linux Slax 9.6.4

There is also a full-flow example script provided at
(tests/test_script.md)[tests/test_script.md] that you can follow to
see and test all functionality.


### Developers

#### Integrating

Hermit needs an external, online wallet application in order to work.
This application has a few ways it may need to integrate with
Hermit:

* Read a public key displayed by Hermit

* Generate a signature request for Hermit (see [examples/signature_requests/bitcoin_testnet.json](examples/signature_requests/bitcoin_testnet.json))

* Read a signature displayed by Hermit (see [examples/signatures/bitcoin.json](examples/signatures/bitcoin.json))

In all cases, Hermit uses the same scheme to encode/decode data into
QR codes.  The pipelines look like this:

  * To create a QR code from a `string`: utf-8 encode -> LZMA-compress -> Base32 encode
  * To parse a QR code `string`: Base32 decode -> LZMA-decompress -> utf-8 decode
  
The `string` data may sometimes itself be JSON.
	
#### Plugins

Hermit allows you to write plugins to extend its functionality.  This
is chiefly so that you can write `Signer` classes for cryptocurrencies
beyond Bitcoin (BTC).

The default directory for plugin code is `/var/lib/hermit`.  Any
`*.py` files in this directory will be loaded by Hermit when it boots
(though you can customize this directory; see the "Configuration"
section above).

An example signer class is below

```python
#
# Example signer class for a putative "MyCoin" currency.  Put in /var/lib/hermit/mycoin_signer.py
#

from hermit.errors import InvalidSignatureRequest
from hermit.signer.base import Signer
from hermit.ui.wallet import wallet_command
import hermit.ui.state as state

# Some library for MyCoin
from mycoin_lib import sign_mycoin_transaction

class MyCoinSigner(Signer):
    """Signs MyCoin transactions"""

    def validate_request(self) -> None:
        """Validates a MyCoin signature request"""
		if 'input' not in self.request:
			raise InvalidSignatureRequest("The param 'input' is required.")
		if 'output' not in self.request:
			raise InvalidSignatureRequest("The param 'input' is required.")
		if 'amount' not in self.request:
			raise InvalidSignatureRequest("The param 'input' is required.")
		# this isn't great validation code, but you get the point...
		
    def display_request(self) -> None:
        """Displays the transaction to be signed"""
        print("""
    INPUT:  {}
	OUTPUT: {}
	AMOUNT: {}
    ...
    SIGNING AS:
    {}""".format(self.input,
                 self.output,
                 self.amount,
				 ...
                 self.bip32_path))
				 
    def create_signature(self) -> None:
        """Signs a transaction"""
		# Here is the magic of MyCoin...
        self.signature = sign_mycoin_transaction(self.input, self.output, ...)

@wallet_command('sign-mycoin')
def sign_mycoin():
    """usage:  sign-mycoin

  Create a signature for a MyCoin transaction.

  Hermit will open a QR code reader window and wait for you to scan an
  Ethereum transaction signature request.

  Once scanned, the details of the signature request will be displayed
  on screen and you will be prompted whether or not you want to sign
  the transaction.

  If you agree, Hermit will open a window displaying the signature as
  a QR code.

  Creating a signature requires unlocking the wallet.

    """
    MyCoinSigner(state.Wallet, state.Session).sign()

```

#### Contributing to Hermit

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

(Linting is done with [flake8] and [mypy].)

[pytest]: https://docs.pytest.org/en/latest/
[flake8]: http://flake8.pycqa.org/en/latest/
[mypy]: http://mypy-lang.org/
[bip32]: https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
