from prompt_toolkit import print_formatted_text, HTML
from json import dumps

from hermit.signer import BitcoinSigner

from .base import command, clear_screen
from .repl import repl
from .shards import ShardCommands, shard_help
import hermit.ui.state as state
from hermit.qrcode import displayer

from typing import Dict


WalletCommands: Dict = {}


def wallet_command(name):
    return command(name, WalletCommands)


@wallet_command("sign-bitcoin")
def sign_bitcoin(unsigned_psbt_b64=''):
    """usage:  sign-bitcoin

    Create a signature for a Bitcoin transaction.

    Can pass in the PSBT via CLI or Hermit will open a QR code reader window and wait for you to scan a Bitcoin transaction signature request.
    TODO: support for QR GIFs.

    Once scanned, the details of the signature request will be displayed
    on screen and you will be prompted whether or not you want to sign
    the transaction.

    If you agree, Hermit will open a window displaying the signature as
    a QR code.

    Creating a signature requires unlocking the wallet.

    """
    BitcoinSigner(
        state.Wallet, state.Session, unsigned_psbt_b64=unsigned_psbt_b64, testnet=state.Testnet,
    ).sign()


def _is_intable(int_as_string):
    # TODO: move me to a util/helper library somewhere
    try:
        int(int_as_string)
        return True
    except Exception:
        return False


def is_valid_bip32_path(path):
    # TODO: move to buidl
    print('one')
    path = path.lower().strip().replace("'", "h").replace("//", "/")  # be forgiving

    print('two')
    if not path.startswith("m/"):
        return False

    print('four')
    sub_paths = path[2:].split("/")
    if len(sub_paths) >= 256:
        # https://bitcoin.stackexchange.com/a/92057
        return False

    print('five')
    for sub_path in sub_paths:
        if sub_path.endswith("h"):
            sub_path = sub_path[:-1]
        if not _is_intable(sub_path):
            return False
        if int(sub_path) >= 2**31:
            # https://bitcoin.stackexchange.com/a/92057
            return False

    print('six')
    return True

@wallet_command("export-xpub")
def export_xpub(path):
    """usage:  export-xpub BIP32_PATH

    Displays the extended public key (xpub) at a given BIP32 path.

    Hermit will open a window displaying the extended public key as a QR
    code.

    Exporting an extended public key requires unlocking the wallet.

    Examples:

      wallet> export-xpub m/45'/0'/0'
      wallet> export-xpub m/44'/60'/2'

    """
    if not is_valid_bip32_path(path):
        raise RuntimeError("Invalid BIP32 Path")
    xpub = state.Wallet.extended_public_key(bip32_path=path, testnet=state.Testnet)
    xfp_hex = state.Wallet.xfp_hex
    title = f"Extended Public Key Info for Seed ID {xfp_hex}"
    xpub_info_text = f"[{xfp_hex}/{path[2:]}]{xpub}"
    # both work, but the json version is less ambiguous (for machine-readable stuff)
    xpub_info_json = dumps({"xfp": xfp_hex, "xpub": xpub, "path": path})
    print_formatted_text(f"\n{title}:\n{xpub_info_text}")
    displayer.display_qr_code(data=xpub_info_json, name=title)


@wallet_command("shards")
def shard_mode():
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

       wallet> help sign-bitcoin
       wallet> help export-xpub

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
      <i>sign-bitcoin</i>
          Produce a signature for a Bitcoin transaction
      <i>sign-echo</i>
          Echo a signature request back as a signature
  <b>KEYS</b>
      <i>export-xpub BIP32_PATH</i>
          Display the extended public key at the given BIP32 path
      <i>export-pub BIP32_PATH</i>
          Display the public key at the given BIP32 path
  <b>WALLET</b>
      <i>unlock</i>
          Explicitly unlock the wallet
      <i>lock</i>
          Explictly lock the wallet
  <b>MISC</b>
      <i>shards</i>
          Enter shards mode
      <i>testnet</i>
          Toggle testnet mode
      <i>debug</i>
          Toggle debug mode
      <i>clear</i>
          Clear screen
      <i>quit</i>
          Exit Hermit

        """
            )
        )


def wallet_repl():
    return repl(WalletCommands, mode="wallet", help_command=wallet_help)
