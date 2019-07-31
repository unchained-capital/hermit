from prompt_toolkit import print_formatted_text

from hermit.signer import (BitcoinSigner,
                           EchoSigner)

from .base import *
from .repl import repl
from .shards import ShardCommands, shard_help
import hermit.ui.state as state

WalletCommands: Dict = {}

def wallet_command(name):
    return command(name, WalletCommands)


@wallet_command('sign-echo')
def echo():
    """usage:  sign-echo

  Scans, "signs", and then displays a QR code.

  Hermit will open a QR code reader window and wait for you to scan a
  QR code.

  Once scanned, the data in the QR code will be displayed on screen
  and you will be prompted whether or not you want to "sign" the
  "transaction".

  If you agree, Hermit will open a window displaying the original QR
  code.

  Agreeing to "sign" does not require unlocking the wallet.

    """
    EchoSigner(state.Wallet, state.Session).sign(testnet=state.Testnet)


@wallet_command('sign-bitcoin')
def sign_bitcoin():
    """usage:  sign-bitcoin

  Create a signature for a Bitcoin transaction.

  Hermit will open a QR code reader window and wait for you to scan a
  Bitcoin transaction signature request.

  Once scanned, the details of the signature request will be displayed
  on screen and you will be prompted whether or not you want to sign
  the transaction.

  If you agree, Hermit will open a window displaying the signature as
  a QR code.

  Creating a signature requires unlocking the wallet.

    """
    BitcoinSigner(state.Wallet, state.Session).sign(testnet=state.Testnet)


@wallet_command('export-xpub')
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
    xpub = state.Wallet.extended_public_key(path)
    name = "Extended public key for BIP32 path {}:".format(path)
    print_formatted_text("\n" + name)
    print_formatted_text(xpub)
    displayer.display_qr_code(xpub, name=name)


@wallet_command('export-pub')
def export_pub(path):
    """usage:  export-pub BIP32_PATH

  Displays the public key at a given BIP32 path.

  Hermit will open a window displaying the public key as a QR code.

  Exporting a public key requires unlocking the wallet.

  Examples:

    wallet> export-pub m/45'/0'/0'/10/20
    wallet> export-pub m/44'/60'/2'/1/12

    """
    pubkey = state.Wallet.public_key(path)
    name = "Public key for BIP32 path {}:".format(path)
    print_formatted_text("\n" + name)
    print_formatted_text(pubkey)
    displayer.display_qr_code(pubkey, name=name)


@wallet_command('shards')
def shard_mode():
    """usage:  shards

  Enter shards mode.

    """
    clear_screen()
    print("You are now in SHARDS mode. Type 'help' for help.\n")
    repl(ShardCommands, mode="shards", help_command=shard_help)


@wallet_command('quit')
def quit_hermit():
    """usage:  quit

  Exit Hermit.

    """
    clear_screen()
    return True


@wallet_command('testnet')
def toggle_testnet():
    """usage:  testnet

  Toggle testnet mode on or off.

  Being in testnet mode changes the way transactions are signed.

  When testnet mode is active, the word TESTNET will appear in
  Hermit's bottom toolbar.

    """
    state.Testnet = not state.Testnet


@wallet_command('help')
def wallet_help(*args,):
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
        print("""
  You are in WALLET mode.  In this mode, Hermit can sign
  transactions and export public keys.

  The following commands are supported (try running `help COMMAND` to
  learn more about each command):

  SIGNING
      sign-bitcoin
          Produce a signature for a Bitcoin transaction
      sign-echo
          Echo a signature request back as a signature
  KEYS
      export-xpub BIP32_PATH
          Display the extended public key at the given BIP32 path
      export-pub BIP32_PATH
          Display the public key at the given BIP32 path
  WALLET
      unlock
          Explicitly unlock the wallet
      lock
          Explictly lock the wallet
  MISC
      shards
          Enter shards mode
      testnet
          Toggle testnet mode
      debug
          Toggle debug mode
      clear
          Clear screen
      quit
          Exit Hermit

        """)

def wallet_repl():
    return repl(WalletCommands, mode='wallet', help_command=wallet_help)
