from typing import Dict
from prompt_toolkit import print_formatted_text, HTML

from hermit.signer import Signer

from ..errors import HermitError
from ..io import (
    read_data_from_animated_qrs, 
    display_data_as_animated_qrs,
)
from .base import command, clear_screen
from .repl import repl
from .shards import ShardCommands, shard_help
import hermit.ui.state as state

from buidl.hd import is_valid_bip32_path
from buidl.libsec_status import is_libsec_enabled

WalletCommands: Dict = {}


def wallet_command(name):
    """Create a new wallet command."""
    return command(name, WalletCommands)

@wallet_command("echo")
def echo():
    """usage:  echo

    Print out the contents of a QR code to screen.

    """
    data = read_data_from_animated_qrs()
    print_formatted_text(data)

@wallet_command("qr")
def qr(data=None):
    """usage:  qr data

    Display an animated QR code containing the given data.
    """
    if data is None:
        raise HermitError("Data is required.")
    display_data_as_animated_qrs(data)

@wallet_command("sign")
def sign(unsigned_psbt_b64=None):
    """usage:  sign [UNSIGNED_PSBT]

    Create a signature for a Bitcoin transaction.

    Will read a base64-encoded unsigned PSBT from the camera.

    Can also pass in the base64-encoded PSBT as a command-line argument.

    Either way, the details of the signature request will be displayed
    on screen and you will be prompted whether or not you want to sign
    the transaction.

    If you agree, Hermit will display the signature.

    Note: Creating a signature requires unlocking the wallet.  If you
    attempt to sign without first unlocking the wallet, Hermit will
    display the signature request and then abort.

    """
    Signer(
        state.Wallet,
        state.Session,
        unsigned_psbt_b64=unsigned_psbt_b64,
        testnet=state.Testnet,
    ).sign()

@wallet_command("export-xpub")
def display_xpub(path=None):
    """usage:  display-xpub [BIP32_PATH]

    Displays the extended public key (xpub) at a given BIP32 path.

    Note: Displaying an xpub requires unlocking the wallet.

    Examples:

      wallet> export-xpub m/48'/0'/0'/2'

    """
    if path is None:
        # Use default paths if none are supplied
        if state.Testnet:
            path = "m/48'/1'/0'/2'"
        else:
            path = "m/48'/0'/0'/2'"
        print_formatted_text(f"No path supplied, using default path {path}...\n")

    if not is_valid_bip32_path(path):
        raise HermitError("Invalid BIP32 path.")

    xpub = state.Wallet.extended_public_key(
        bip32_path=path, testnet=state.Testnet, use_slip132=True
    )
    xfp_hex = state.Wallet.xfp_hex
    title = f"Extended Public Key Info for Seed ID {xfp_hex}"
    xpub_info_text = f"[{xfp_hex}/{path[2:]}]{xpub}"
    # TODO: offer to save this json file somewhere?
    # xpub_info_json = json.dumps({"xfp": xfp_hex, "xpub": xpub, "path": path})
    print_formatted_text(f"\n{title}:\n{xpub_info_text}")
    display_data_as_animated_qrs(xpub_info_text)


# @wallet_command("set-account-map")
# def set_account_map(account_map_str=""):
#     """usage:  set-account-map

#     Sets the account map (for change and receiving address validation) with the collection of public key records that you get from your Coordinator software

#     The account map can be supplied via CLI, or if left blank the camera will open to scan the account map from you Coordinator software.

#     Examples:

#       wallet> set-account-map
#       wallet> set-account-map wsh(sortedmulti(2,[deadbeef/48h/0h/0h/2h]Zpub...))

#     """
#     # FIXME: this should be persisted, but persistance is currently written using dangerous os.system() calls and only stored at the shards level (not the wallet level)
#     # A major persistence refactor is needed

#     if (
#         state.Wallet.set_account_map(
#             account_map_str=account_map_str, testnet=state.Testnet
#         )
#         is True
#     ):
#         print_formatted_text("Account map set")
#     else:
#         print_formatted_text("Account map NOT set")
#         # TODO: this is an ugly hack to get around the fact that we store xpriv/tpriv (which has a version byte), but what we really want to store is the secret (mnemonic)
#         # Get rid of this in the future when Hermit state overhaul is complete
#         state.Wallet.lock()


# @wallet_command("display-address")
# def display_address(offset=0, limit=10, is_change=0):
#     """usage:  display-address

#     Display bitcoin address(es) that belong to your account map.
#     By default, this will display the first 10 addresses on the receive branch.

#     You can customize the offset, limit, and the receive/change branch as follows.

#     Examples:

#       wallet> display-address
#       wallet> display-address 4 5 1

#     """
#     if not state.Wallet.quorum_m or not state.Wallet.pubkey_records:
#         print_formatted_text(
#             "Account map not previously set. Please use set-account-map first to set an account map that we can derive bitcoin addresses from"
#         )
#         return

#     # Format params
#     offset = int(offset)
#     limit = int(limit)
#     is_change = bool(is_change)
#     testnet = state.Testnet

#     to_print = f"{state.Wallet.quorum_m}-of-{len(state.Wallet.pubkey_records)} Multisig {'Change' if is_change else 'Receive'} Addresses"
#     if not is_libsec_enabled():
#         # TODO: use libsec bindings in buidl for 100x performance increase
#         to_print += "\n(this is ~100x faster if you install libsec)"
#     print_formatted_text(to_print + ":")
#     generator = state.Wallet.derive_child_address(
#         testnet=testnet, is_change=is_change, offset=offset, limit=limit
#     )
#     for cnt, address in enumerate(generator):
#         print_formatted_text(f"#{cnt + offset}: {address}")


@wallet_command("shards")
def enter_shard_mode():
    """usage:  shards

    Enter shards mode.

    """
    clear_screen()
    print("You are now in SHARDS mode. Type 'help' for help.\n")
    repl(ShardCommands, mode="shards", help_command=shard_help)


@wallet_command("quit")
def quit_hermit():
    """usage:  quit

    Exit Hermit.

    """
    clear_screen()
    return True


@wallet_command("testnet")
def toggle_testnet():
    """usage:  testnet

    Toggle testnet mode on or off.

    Being in testnet mode changes the way transactions are signed.

    When testnet mode is active, the word TESTNET will appear in
    Hermit's bottom toolbar.

    """
    state.Testnet = not state.Testnet


@wallet_command("help")
def wallet_help(
    *args,
):
    """usage: help [COMMAND]

    Prints out helpful information about Hermit's "wallet" mode (the
    default mode).

    When called with an argument, prints out helpful information about
    the command with that name.

    Examples:

       wallet> help sign
       wallet> help display-xpub

    """
    if len(args) > 0 and args[0] in WalletCommands:
        print(WalletCommands[args[0]].__doc__)
    else:
        print_formatted_text(
            HTML(
                """
  You are in WALLET mode.  In this mode, Hermit can sign
  transactions and export public keys.

  The following commands are supported (try running `help COMMAND` to
  learn more about each command):

  <b>SIGNING</b>
      <i>sign</i>
          Produce a signature for a Bitcoin transaction
  <b>KEYS</b>
      <i>display-xpub [BIP32_PATH]</i>
          Display the extended public key at the given BIP32 path
      <i>display-pub [BIP32_PATH]</i>
          Display the public key at the given BIP32 path
  <b>WALLET</b>
      <i>unlock</i>
          Explicitly unlock the wallet
      <i>lock</i>
          Explictly lock the wallet
  <b>TESTING</b>
      <i>echo</i>
          Print data read from the camera to the screen
      <i>qr DATA</i>
          Display the given DATA in an animated QR code sequence
  <b>MODES</b>
      <i>shards</i>
          Enter shards mode
      <i>testnet</i>
          Toggle testnet mode
      <i>debug</i>
          Toggle debug mode
  <b>MISC</b>
      <i>clear</i>
          Clear screen
      <i>quit</i>
          Exit Hermit

        """
            )
        )

def wallet_repl():
    """Start a REPL in wallet mode."""
    return repl(WalletCommands, mode="wallet", help_command=wallet_help)
