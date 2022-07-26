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
No shards.
shards> build-family-from-phrase              # create new shard family from BIP39 phrase
...
How many groups are required unlock (P)? 1    # use a single group
...
What is m of n for Group 1? 2of3              # 2of3 shards
What is m of n for Group 2?                   # hit ENTER
...

Enter BIP39 phrase for wallet below (CTRL-D to submit):

merge alley lucky axis penalty manage         # enter BIP39 phrase
latin gasp virus captain wheel deal
chase fragile chapter boss zero dirt
stadium tooth physical valve kid plunge
                                              # CTRL-D to submit


Enter at least 256 bits worth of random data.

Hit CTRL-D when done.

Collected   0.0 bits>:awef;oaweo;fawe         # mash the keyboard
Collected  38.3 bits>:awefa;wef;oawefaawe;faweaw
Collected 102.0 bits>:aw;efjao;ejwf;oaje;fjao;web
Collected 189.3 bits>:bsblsrevhlerferfrefserfuulfli
Collected 333.2 bits>:                        # CTRL-D to submit

Family: 515, Group: 1, Shard: 1
Enter name: alice                             # name the first shard
new password> ********                        # and provide a password
     confirm> ********

Family: 515, Group: 1, Shard: 2               # repeat for second shard
Enter name: bob
new password> ********
     confirm> ********
 shards> list-shards                          # see newly created shards
     alice (family:515 group:1 member:1)
     bob (family:515 group:1 member:2)

shards> write                                 # save newly created shards to disk
shards> quit                                  # back to wallet mode
wallet> unlock                                # unlock the shards we just created
Choose shard
(options: alice, bob or <enter> to quit)
>  alice                                      # pick the first shard and provide password

Enter password for shard alice (family:515 group:1 member:1)
password> ********
Choose shard
(options: bob or <enter> to quit)
> bob                                         # repeat for second shard

Enter password for shard bob (family:515 group:1 member:2)
password> ********
*wallet>                                      # wallet is now unlocked
*wallet> sign                                 # sign a bitcoin transaction by scanning a QR code

...

# See tests/fixtures/signature_requests/2-of-2.p2sh.testnet.gif for example transaction request QR code
```

Setup
-----

## Dependencies

Hermit requires Python > 3.5.

## Installation

Installing Hermit can be done via `pip3`:

```
$ pip3 install hermit
```

If you want to develop against Hermit, see the "Developers" section
below for a different way of installing Hermit.

## Configuration

Hermit's default configuration works fine for initial evaluation but
is not designed for production usage.

For production usage, you'll want to configure Hermit through its
configuration file.

By default, Hermit looks for a configuration file at
`/etc/hermit.yml`, but you can change this by passing in a different
configuration file path through an environment variable when you
launch `hermit`:

```
$ HERMIT_CONFIG=/path/to/hermit.yml hermit
```

See the documentation for the `HermitConfig` class for details on
allowed configuration settings.

Usage
-----

To start Hermit, just run the `hermit` command.

```
$ hermit
```

### "Wallet" Functions

As stated above, Hermit is not a "wallet" but it does perform some key
functions associated with bitcoin wallets: signing bitcoin
transactions and exporting extended public keys.

#### Signing Transactions

Assuming Hermit has a private key (see the "Private Key Management"
section below), you can run the following commands to unlock it and
sign a bitcoin transaction:

```
wallet> unlock
...
wallet> sign

# See tests/fixtures/signature_requests/2-of-2.p2sh.testnet.gif for example transaction request
```

If you don't unlock the private key first, Hermit will preview the
transaction for you and abort signing.

Remember: Hermit does not create transactions.  An external
coordinator application must pass Hermit an unsigned
[PSBT](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)
which Hermit interprets.

You can find examples of such requests in
[tests/fixtures/signature_requests](tests/fixtures/signature_requests).

#### Exporting Extended Public Keys (xpubs)

Hermit can export extended public keys (xpubs) derived from a private
key.

```
wallet> unlock
wallet> display-xpub m/45'/0'/0'
xpub...
```

Extended public keys are printed to screen and displayed as QR codes.

### Private key management

Before Hermit can be used for "wallet" functionality, you must first
define some private keys for Hermit to store & protect.

Hermit stores all private keys in a sharded format.

Sharding is done using
[SLIP-0039](https://github.com/satoshilabs/slips/blob/master/slip-0039.md)
which means there are two levels of structure:

* Groups -- some quorum *P* of *Q* groups is required to unlock a key

* Shards -- some quorum *m* of *n* shards is required to unlock
  each group, with *m* and *n* possibly different for each group

This structure creates a lot of flexibility for different scenarios.
For example:

* With *P=Q=1* and *n=m=1*, SLIP-0039 only a single shard is used,
  replicating a singlesig wallet.  This is useful for testing but not
  the expected usage pattern.

* With *P=Q=1*, SLIP-0039 reproduces *m* of *n* Shamir sharding with
  *n* shards, *m* of which are required to unlock the private key.

* *P=Q=1*; one 'junior' group with *m=4$ and *n=7*, and another
  'senior' group with *m=2* and *n=3*.  This structure requires
  **either** 4 of 7 'junior' shards **OR** 2 of 3 'senior' shards to
  unlock the private key.

Hermit extends the current SLIP-39 proposal by encrypting each shard
with a password.  This allows each shard to be "assigned" to a given
operator who knows that shard's password.  A quorom of such operators
must physically co-locate and decrypt their shards by entering their
passwords before Hermit can unlock the corresponding private key.

Shard encryption can be skipped by providing an empty string as the
password when creating a shard (or changing the password on the
shard).  While this makes the storage of the shard less secure, it
does make it possible to export the shards to technologies that
support only unencrypted SLIP-39 implementations (e.g. Trezor).

#### Random number generation

Secure encryption and sharding requires generating cryptographically
random values.  **Hermit does not generate its own random values**.

Instead, Hermit expects you to choose a trusted source of randomness
and manually enter random values from it:

```
Enter at least 256 bits worth of random data.

Hit CTRL-D when done.

Collected   0.0 bits>: 
```

Two simple ways to do this are to roll fair dice or draw cards from a
well-shuffled deck and transcribe the resulting values.

The number of random bits Hermit requires is determined by the action
you are taking.  The larger the shard families you're working with,
the more randomness is required.

The characters you enter can be chosen from any character set you
like, as appropriate for your chosen method of generation.  If you are
rolling dice, for example, all the characters you enter will be digits
from 1 through 6.  Hermit will use the concatenated bytes of the
complete text you enter as its final random value.

The number of characters you'll need to enter to reach the required
number of random bits will depend on the character set produced by
your chosen random number generator.

As you enter characters, hermit will estimate the number of bits of
randomness you have entered so far but this estimate **should not be
relied upon** for production usage.  It is better to **predetermine**
the number of characters you need to enter based on the number of
random bits Hermit is asking for and size of the character set used by
your chosen random number generator.

For example, a single roll of a fair 6-sided die produces
log<sub>2</sub>(6) ~ 2.58 bits of randomness.  This means that ~100
dice rolls are required to produce 256 bits of randomness.

Note, when testing Hermit it is easiest to simply "mash" on the
keyboard till sufficient "random" bits are detected by Hermit.  This
is obviously not a good idea in production!

#### Create a shard family for a new private key

A new private key can be created by entering random data through the
keyboard:

```
wallet> shards
shards> build-family-from-random
```

You will be prompted for the configuration to use for the shard family:

```
How many groups should be required to unlock the wallet (P)? 1
...
What shard configuration should be used for Group 1? 2of3
What shard configuration should be used for Group 2?
...
```

and then for sufficient random data to create both the new private key
and the shard family.

You'll then be asked to name each shard and provide a password for it.

```
Family: 8347, Group: 1, Shard: 1
Enter name: alice
...
Family: 8347, Group: 1, Shard: 2
Enter name: bob
...
Family: 8347, Group: 1, Shard: 3
Enter name: charlie
...
```

Finally, don't forget to store this information on disk!

```
shards> write
```

#### Create a shard family for a private key imported from a BIP39 phrase

If you are using a non-sharded wallet such as a hardware wallet
(Trezor, Ledger, Coldcard, Electrum, &c.), you can import your private
key from your
[BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki)
"seed phrase" and Hermit will shard it for you.

```
wallet> shards
shards> build-family-from-phrase
```

Similar to creating a shard family from a new private key, you'll be
prompted for the configuration to use for the new shard family.

You'll next be prompted to enter the BIP39 phrase:

```
Enter BIP39 phrase for wallet below (CTRL-D to submit):
merge alley lucky axis penalty manage
latin gasp virus captain wheel deal
chase fragile chapter boss zero dirt
stadium tooth physical valve kid plunge
```

and then prompted to enter random data to create the shard family.
You'll then be asked to name each shard and provide a password.

**Note:** Hermit will **not** export private keys as BIP39 phrases.
It will only export shards as encrypted SLIP39 phrases.  This means it
is challenging to extract a key from a Hermit installation for use in,
for example, a hardware wallet or Electrum.  This constraint is
present by design.

#### Create a new shard family from an existing shard family

A private key already stored in Hermit can be resharded into a
different configuration of groups and/or shards.

```
wallet> shards
shards> build-family-from-family
```

You'll first be asked to unlock the existing shard family:

```
Choose shard
...
> alice
...
> bob
```

You'll next be prompted for the configuration to use for the new shard
family and sufficient random data to build it.  You'll then be asked
to name each new shard and provide a password.

### Shard management

Hermit provides several commands for manipulating individual shards
within shard families.

#### Importing & exporting shards

Shards can be individually imported & exported, which allows
transferring entire shard families between Hermit installations.

Transferring can be done through QR codes or through encrypted
SLIP-0039 phrases.

To transfer the shard `alice` using QR codes, begin on the Hermit
installation that already has the shard:

```
wallet> shards
shards> export-shard-as-qr alice
```

This Hermit installation will display a QR code.  On the other Hermit
installation run

```
wallet> shards
shards> import-shard-from-qr alice
```

This Hermit installation will open its camera.  Scan the QR code from
the first Hermit installation to complete the transfer.

Note that the **name** of the shard can be changed during transfer but
the shard's data and password are always transferred unchanged.

To transfer the same shard using SLIP-0039 phrases, again begin on the
Hermit installation that already has the shard:

```
wallet> shards
shards> export-shard-as-phrase alice

Encrypted SLIP39 phrase for shard alice:

friar merchant academic academic analysis ...
```

On the second Hermit installation run

```
wallet> shards
shards> import-shard-from-phrase alice

Enter SLIP39 phrase for shard alice below (CTRL-D to submit):
```

Type in the SLIP-0039 phrase and hit `CTRL-D` to complete the
transfer.

#### Renaming, copying, and deleting shards

Shards can renamed without knowing their passwords:

```
shards> list-shards
     alpha-alice (family:10014 group:1 member:1)
     alpha-bob (family:10014 group:1 member:2)
     alpha-charlie (family:10014 group:1 member:3)
shards> rename-shard alpha-bob alpha-bobby
shards> list-shards
     alpha-alice (family:10014 group:1 member:1)
     alpha-bobby (family:10014 group:1 member:2)
     alpha-charlie (family:10014 group:1 member:3)
```

Shards can also be copied:

```
shards> list-shards
     alpha-alice (family:10014 group:1 member:1)
     alpha-bobby (family:10014 group:1 member:2)
     alpha-charlie (family:10014 group:1 member:3)
shards> copy-shard alpha-charlie alpha-dave
```

**WARNING:** When copying a shard, you'll be asked for the current
password to the existing shard as well as a new password for the new
shard.  You'll also be forced to unlock Hermit and you MUST select the
new shard when doing so.  Run `help copy-shard` while in `shards` mode
for further information.

Shards can also be deleted, which is useful after copying them:

```
shards> list-shards
     alpha-alice (family:10014 group:1 member:1)
     alpha-bobby (family:10014 group:1 member:2)
     alpha-charlie (family:10014 group:1 member:3)
     alpha-dave (family:10014 group:1 member:3)
shards> delete-shard alpha-charlie
Really delete shard alpha-charlie? yes
shards> list-shards
     alpha-alice (family:10014 group:1 member:1)
     alpha-bobby (family:10014 group:1 member:2)
     alpha-dave (family:10014 group:1 member:3)
```

Anytime you manipulate shards, don't forget to store this information
on disk!

```
shards> write
```

#### Shard storage

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
from the filesystem to the TPM/HSM.

When Hermit first boots, shards from the TPM/HSM or filesystem (in
that order) are loaded into memory.  The `restore` command can be used
to reload shards from the TPM/HSM into memory.

See the documentation for `HermitConfig.DefaultCommands` for more
details on shard persistence.

By default, Hermit "fakes" a TPM/HSM by using the filesystem,
e.g. running `persist` will copy (and compress) the `shards_file` to
the same location with a suffix `.persisted` added.

#### Shard Rotation

The commands Hermit provides for manipulating shards and shard
families allow for transferring shards between operators.

##### Recovering from the loss of a shard or operator

Begin with a key named `cherry` managed by three operators `a`, `b`,
and `c` in a 2-of-3 configuration.

```
wallet> shards
shards> list-shards
     cherry-a (family:10014 group:1 member:1)
     cherry-b (family:10014 group:1 member:2)
     cherry-c (family:10014 group:1 member:3)
```

Our goal is to replace the operator/shard `c` with a new
operator/shard `d`.

We begin by building a new shard family:

```
shards> build-family-from-family
...
```

which will require unlocking the original family:

```
Choose shard
...
> cherry-a
...
> cherry-b
```

We'll use the same 2-of-3 configuration for the new family as for the old:

```
How many groups should be required to unlock the wallet (P)? 1
...
What shard configuration should be used for Group 1? 2of3
What shard configuration should be used for Group 2?
...
```

After entering sufficient random data, we'll now be able to define the
new shards.  We'll start with shards for the operators `a` and `b`
that are shared between the old and new shard families (these
operators can even use the same passwords for their new shards as they
used for their old shards, if desired):

```
Family: 8347, Group: 1, Shard: 1
Enter name: cherry-a-copy
...
Family: 8347, Group: 1, Shard: 2
Enter name: cherry-b-copy
...
```

The final shard will go to the new operator `d`:

```
Family: 8347, Group: 1, Shard: 3
Enter name: cherry-d
...
```

Now there are two simultaneous shard families for the key `cherry`:

* the original 2-of-3 among `a`, `b`, and `c` 
* the new 2-of-3 among `a`, `b`, and `d`

```
shards> list-shards
     cherry-a (family:10014 group:1 member:1)
     cherry-b (family:10014 group:1 member:2)
     cherry-c (family:10014 group:1 member:3)
     cherry-a-copy (family:8347 group:1 member:1)
     cherry-b-copy (family:8347 group:1 member:2)
     cherry-d (family:8347 group:1 member:3)
```

The old shard family can now be deleted:

```
shards> delete-shard cherry-a
Really delete shard cherry-a? yes
shards> delete-shard cherry-b
Really delete shard cherry-b? yes
shards> delete-shard cherry-c
Really delete shard cherry-c? yes
```

Which leaves just the new shard family, without operator/shard `c`:

```
shards> list-shards
     cherry-a-copy (family:8347 group:1 member:1)
     cherry-b-copy (family:8347 group:1 member:2)
     cherry-d (family:8347 group:1 member:3)
```

The shards for operators `a` and `b` can be renamed if desired:

```
shards> rename-shard cherry-a-copy cherry-a
shards> rename-shard cherry-b-copy cherry-b
shards> list-shards
     cherry-a (family:8347 group:1 member:1)
     cherry-b (family:8347 group:1 member:2)
     cherry-d (family:8347 group:1 member:3)
```

Finally, don't forget to store this information on disk!

```
shards> write
```

The procedure above requires all the operators of the new shard family
(`a`, `b`, and `d`) but only a quorum of operators from the original
shard family (`a` and `b`).  Crucially, this means the procedure can
be performed **without** the participation of operator being replaced
(`c`).  This allows recovering from scenarios where an operator has
forgotten their shard password or has become unavailable or
uncooperative.

Because of the SLIP39 sharding, a rogue operator who has exfiltrated
their own decrypted shard cannot use that information to learn
anything about the old or new shard families.


Development
-----------

### Setup

Hermit has the following development dependencies:

* Python >= 3.5
* `make` for running development tasks

### Installation

Developers will want to clone a copy of the Hermit source code:

```
$ git clone https://github.com/unchained-capital/hermit
$ cd hermit
$ make
```

### Usage

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

### Contributing

Unchained Capital welcomes bug reports, new features, and better
documentation for Hermit.  To contribute, create a pull request (PR)
on GitHub against the [Unchained Capital fork of
Hermit](https://github.com/unchained-capital/hermit).

Before you submit your PR, make sure to run the test suite and static
analysis tools:

```
$ source environment.sh
$ make check test
```
