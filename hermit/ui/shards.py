from base64 import b64encode, b64decode

from prompt_toolkit import print_formatted_text, HTML

from ..io import (
    read_data_from_animated_qrs,
    display_data_as_animated_qrs,
)
from .base import command, clear_screen, disabled_command
from ..config import get_config
import hermit.ui.state as state

from typing import Dict, List


ShardCommands: Dict = {}

DisabledShardsCommands: List[str] = get_config().disabled_shards_commands


def shard_command(name):
    if name not in DisabledShardsCommands:
        return command(name, ShardCommands)
    else:
        return disabled_command(name, ShardCommands)


#
# Families
#


@shard_command("build-family-from-phrase")
def build_family_from_phrase():
    """usage: build-family-from-phrase

    Build a shard family from a BIP39 mnemonic phrase.

    Hermit will prompt you in turn for a shard configuration, a BIP39
    phrase, and random data from which to build shards.

    Once the shards have been built, Hermit will ask you to name each
    one and encrypt it with a password.

    These shards will be built in memory. You should run `write` to save
    the shards to the filesystem.

    """
    state.Wallet.shards.create_share_from_wallet_words()


@shard_command("build-family-from-random")
def build_family_from_random():
    """usage: build-family-from-random

    Build a shard family from random data.

    Hermit will prompt you for a shard configuration and then for random
    data to use in building the shards.

    Once the shards have been built, Hermit will ask you to name each
    one and encrypt it with a password.

    These shards will be built in memory. You should run `write` to save
    the shards to the filesystem.

    """
    state.Wallet.shards.create_random_share()


@shard_command("build-family-from-family")
def build_family_from_family():
    """usage:  build-family-from-family

    Rebuild a shard family from an existing family.

    Hermit will prompt you to unlock a particular shard family, ask
    you to provide configuration for a new family, and random data to
    use in building the new shards.

    Once the shards have been built, Hermit will ask you to name each
    one and encrypt it with a password.

    These shards will be built in memory. You should run `write` to save
    the shards to the filesystem.

    Running this command will first lock the wallet, forcing you to
    unlock it again.

    """
    state.Wallet.lock()
    state.Wallet.shards.reshard()


# This is dangerous?
#
# @shard_command('export-wallet-as-phrase')
# def export_wallet_as_phrase():
#     """usage:  export-wallet-as-phrase

#   Print the BIP39 mnemonic phrase for the current wallet.

#   Running this command will first lock the wallet, forcing you to
#   unlock it again.

#     """
#     state.Wallet.lock()
#     state.Wallet.shards.reveal_wallet_words()


#
# Shards
#


@shard_command("list-shards")
def list_shards():
    """usage:  list-shards

    List all shards.

    """
    state.Wallet.shards.list_shards()


@shard_command("import-shard-from-phrase")
def import_shard_from_phrase(name):
    """usage:  import-shard-from-phrase NAME

    Import a shard from an encrypted SLIP39 mnemonic phrase.

    The password for the shard will be the one encoded into the phrase.

    The shard is imported in memory.  You must run the `write` command
    to save shards to the filesystem.

    Examples:

      shards> import-shard-from-phrase shard1
      ...
      shards> write

    """
    state.Wallet.shards.input_shard_words(name)


@shard_command("import-shard-from-qr")
def import_shard_from_qr(name):
    """usage import-shard-from-qr NAME

    Import a shard from a QR code.

    The shard is imported in memory.  You must run the `write` command
    to save shards to the filesystem.

    Examples:

      shards> import-shard-from-qr shard1
      ...
      shards> write

    """
    qr_data = read_data_from_animated_qrs()
    shard_data = b64decode(qr_data)
    state.Wallet.shards.import_shard_qr(name, shard_data)


@shard_command("export-shard-as-phrase")
def export_shard_as_phrase(name):
    """usage:  export-shard-as-phrase NAME

    Print the encrypted SLIP39 mnemonic phrase for the given shard.

    """
    state.Wallet.shards.reveal_shard(name)


@shard_command("export-shard-as-qr")
def export_shard_as_qr(name):
    """usage export-shard-as-qr NAME

    Display a QR code for the given shard.

    """
    shard_data = b64encode(state.Wallet.shards.qr_shard(name)).decode("utf-8")
    display_data_as_animated_qrs(base64_data=shard_data)


@shard_command("copy-shard")
def copy_shard(old, new):
    """usage:  copy-shard OLD NEW

    Copy a shard while assigning it a new password.  You will also
    have to provide the current password for the original shard.

    The new shard is created in memory.  You must run the `write`
    command to save the new shard to the filesystem.

    WARNING: The current password for the original shard cannot be
    validated in isolation; if you accidentally enter the wrong
    password for the existing shard the new shard will be corrupted.

    To avoid this outcome, this command will initiate an immediate
    `unlock` of the wallet.  When unlocking, you MUST select the newly
    created shard as one of the shards you use to unlock the family.
    See the example below for details:

    Example:

      shards> list-shards
        alice (family:17489 group:1 member:1)
        bob (family:17489 group:1 member:2)
      shards> copy-shard alice alice-copy

      Change password for shard alice-copy (family:17489 group:1 member:2)
      old password> ********
      new password> ********
      confirm> ********
      Choose shard
      (options: alice, bob, alice-copy or <enter> to quit)
      > alice-copy
      Enter password for shard foo-2-copy (family:17489 group:1 member:2)
      password> ********
      Choose shard
      (options: bob or <enter> to quit)
      > bob
      Enter password for shard foo-1 (family:17489 group:1 member:1)
      password> ********
      *shards>
      shards> list-shards
        alice (family:17489 group:1 member:1)
        alice-copy (family:17489 group:1 member:1)
        bob (family:17489 group:1 member:2)
      *shards> write

    """
    state.Wallet.shards.copy_shard(old, new)
    state.Wallet.lock()
    state.Wallet.unlock(testnet=state.Testnet)


@shard_command("rename-shard")
def rename_shard(old, new):
    """usage:  rename-shard OLD NEW

    Rename a shard.  This does not change the shard's data or
    password.

    The change is made in memory.  You must run the `write` command to
    save the change to the filesystem.

    Examples:

      shards> rename-shard apple pear
      shards> write

    """
    state.Wallet.shards.rename_shard(old, new)


@shard_command("delete-shard")
def delete_shard(name):
    """usage:  delete_shard NAME

    Delete a shard.

    Hermit will prompt you to confirm whether or not you really want to
    delete the given shard.

    If you agree, the shard will be deleted in memory.  You must run the
    `write` command to delete the shard from the filesystem.

    Examples:

      shards> delete-shard apple
      ...
      shards> write

    """
    state.Wallet.shards.delete_shard(name)


#
# Storage
#


@shard_command("write")
def write():
    """usage:  write

    Write all shards in memory to the filesystem.

    Metadata (number of shards, shard numbers and names) will be written
    in plain text but all shard content will be encrypted with each
    shard's password.

    You may want to run the `persist` command after running the `write`
    command.

    """
    state.Wallet.shards.save()


@shard_command("persist")
def persist():
    """usage:  persist

    Copies shards from the filesystem to persistent storage.

    Persistent storage defaults to the filesystem but can be configured
    to live in a higher-security location such as a Trusted Platform
    Module (TPM).

    """
    state.Wallet.shards.persist()


@shard_command("backup")
def backup():
    """usage:  backup

    Copies shards from the filesystem to backup storage.

    Backup storage defaults to the filesystem but can be configured as
    necessary.

    """
    state.Wallet.shards.backup()


@shard_command("restore")
def restore():
    """usage:  restore

    Copies shards from backup storage to the filesystem.

    """
    state.Wallet.shards.restore()


@shard_command("reload")
def reload():
    """usage:  reload

    Reload shards in memory from the filesystem.

    This resets any changes made to shards in memory during the current
    session.

    """
    state.Wallet.lock()
    state.Wallet.shards.reload()


# @shard_command('clear')
# def clear():
#     """usage:  clear

#   Clear shards from memory.

#   DANGER: If you run the `write` command, shards will be deleted
#   from the filesystem storage, too.

#     """
#     state.Wallet.shards.clear_shards()


# @shard_command('initialize')
# def initialize():
#     """usage: initialize

#   (Re-)initialize shards in memory and in the filesystem.

#     """
#     state.Wallet.shards.initialize_file()


#
# Other
#


@shard_command("quit")
def quit_shards():
    """usage:  quit

    Exit shards mode."""
    clear_screen()
    print("You are now in WALLET mode.  Type 'help' for help.\n")
    return True


@shard_command("help")
def shard_help(
    *args,
):
    """usage: help [COMMAND]

    Prints out helpful information about Hermit's "shards" mode.

    When called with an argument, prints out helpful information about
    the command with that name.

    Examples:

       shards> help import-shard-from-phrase
       shards> help build-shards-from-random

    """
    if len(args) > 0 and args[0] in ShardCommands:
        print(ShardCommands[args[0]].__doc__)
    else:
        print_formatted_text(
            HTML(
                """
  You are in SHARDS mode.  In this mode, Hermit can create and
  manipulate shards and interact with storage.

  The following commands are supported (try running `help COMMAND` to
  learn more about each command):

  <b>SHARD FAMILIES</b>
      <i>build-family-from-phrase</i>
           Create a shard family from a BIP39 mnemonic phrase
      <i>build-family-from-random</i>
           Create a shard family from random data
      <i>build-family-from-family</i>
           Create a shard family from an existing family
  <b>SHARDS</b>
      <i>list-shards</i>
          List all existing shards
      <i>import-shard-from-phrase NAME</i>
          Input a new shard from an encrypted SLIP39 mnemonic phrase
      <i>import-shard-from-qr NAME</i>
          Input a new shard from a QR code
      <i>export-shard-as-phrase NAME</i>
          Display the given shard as an encrypted SLIP39 mnemonic phrase
      <i>export-shard-as-qr NAME</i>
          Display the given shard as a QR code
      <i>copy-shard OLD NEW</i>
          Copy an existing shard with a new password
      <i>rename-shard OLD NEW</i>
          Rename an existing shard with a new name
      <i>delete-shard NAME</i>
          Delete a shard
  <b>STORAGE</b>
      <i>write</i>
          Copy shards from memory to the filesystem
      <i>persist</i>
          Copy shards from the filesystem to the data store
      <i>backup</i>
          Copy shards from filesystem to backup storage
      <i>restore</i>
          Copy shards from backup storage to filesystem
      <i>reload</i>
          Copy shards from the filesystem into memory
  <b>WALLET</b>
      <i>unlock</i>
          Explicitly unlock the wallet
      <i>lock</i>
          Explictly lock the wallet
  <b>MISC</b>
      <i>debug</i>
          Toggle debug mode
      <i>clear</i>
          Clear screen
      <i>quit</i>
          Return to wallet mode

        """
            )
        )
