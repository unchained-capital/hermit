from prompt_toolkit import print_formatted_text, HTML

from hermit.signer import BitcoinSigner

from .base import command, clear_screen
from .repl import repl
from .shards import ShardCommands, shard_help
import hermit.ui.state as state
from hermit.qrcode import displayer, reader

from buidl.hd import is_valid_bip32_path
from buidl.libsec_status import is_libsec_enabled

from typing import Dict
from hermit.qrcode import reader


WalletCommands: Dict = {}


def wallet_command(name):
    return command(name, WalletCommands)

@wallet_command("echo")
def echo_qr(unsigned_psbt_b64=""):
    """usage:  echo

    Print out the contents of a QR code.

    """
    data = reader.read_qr_code("Scan data to echo")
    print_formatted_text(data)

@wallet_command("qr")
def create_qr(data=""):
    """usage:  qr data

    Display an animated QR code containing the given data.
    """
    displayer.display_qr_code(data=data, name="QR Code")

@wallet_command("sign-bitcoin")
def sign_bitcoin(unsigned_psbt_b64=""):
    """usage:  sign-bitcoin

    Create a signature for a Bitcoin transaction.

    Can pass in the PSBT via CLI or Hermit will open a QR code reader window and wait for you to scan a Bitcoin transaction signature request.

    Once scanned, the details of the signature request will be displayed
    on screen and you will be prompted whether or not you want to sign
    the transaction.

    If you agree, Hermit will open a window displaying the signature as
    a QR code.

    Creating a signature requires unlocking the wallet.

    """

    if not unsigned_psbt_b64:
        # Get unsigned PSBT from webcam (QR gif) if not already passed in as an argument
        unsigned_psbt_b64 = reader.read_qr_code("Scan the psbt.")

    try:
        BitcoinSigner(
            state.Wallet,
            state.Session,
            unsigned_psbt_b64=unsigned_psbt_b64,
            testnet=state.Testnet,
        ).sign()
    except Exception as e:
        print_formatted_text(e)

@wallet_command("export-xpub")
def export_xpub(path=""):
    """usage:  export-xpub BIP32_PATH

    Displays the extended public key (xpub) at a given BIP32 path.

    Hermit will open a window displaying the extended public key as a QR
    code.

    Exporting an extended public key requires unlocking the wallet.
    TODO: this shouldn't be a requirement

    Examples:

      wallet> export-xpub m/48'/0'/0'/2'

    """
    if not path:
        # Use default paths if none are supplied
        if state.Testnet:
            path = "m/48'/1'/0'/2'"
        else:
            path = "m/48'/0'/0'/2'"
        print_formatted_text(f"No path supplied, using default path {path}...\n")

    if not is_valid_bip32_path(path):
        raise RuntimeError("Invalid BIP32 Path")

    xpub = state.Wallet.extended_public_key(
        bip32_path=path, testnet=state.Testnet, use_slip132=True
    )
    xfp_hex = state.Wallet.xfp_hex
    title = f"Extended Public Key Info for Seed ID {xfp_hex}"
    xpub_info_text = f"[{xfp_hex}/{path[2:]}]{xpub}"
    # TODO: offer to save this json file somewhere?
    # xpub_info_json = json.dumps({"xfp": xfp_hex, "xpub": xpub, "path": path})
    print_formatted_text(f"\n{title}:\n{xpub_info_text}")
    displayer.display_qr_code(data=xpub_info_text, name=title)


@wallet_command("set-account-map")
def set_account_map(account_map_str=""):
    """usage:  set-account-map

    Sets the account map (for change and receiving address validation) with the collection of public key records that you get from your Coordinator software

    The account map can be supplied via CLI, or if left blank the camera will open to scan the account map from you Coordinator software.

    Examples:

      wallet> set-account-map
      wallet> set-account-map wsh(sortedmulti(2,[deadbeef/48h/0h/0h/2h]Zpub...))

    """
    # FIXME: this should be persisted, but persistance is currently written using dangerous os.system() calls and only stored at the shards level (not the wallet level)
    # A major persistence refactor is needed

    if (
        state.Wallet.set_account_map(
            account_map_str=account_map_str, testnet=state.Testnet
        )
        is True
    ):
        print_formatted_text("Account map set")
    else:
        print_formatted_text("Account map NOT set")
        # TODO: this is an ugly hack to get around the fact that we store xpriv/tpriv (which has a version byte), but what we really want to store is the secret (mnemonic)
        # Get rid of this in the future when Hermit state overhaul is complete
        state.Wallet.lock()


@wallet_command("display-address")
def display_address(offset=0, limit=10, is_change=0):
    """usage:  display-address

    Display bitcoin address(es) that belong to your account map.
    By default, this will display the first 10 addresses on the receive branch.

    You can customize the offset, limit, and the receive/change branch as follows.

    Examples:

      wallet> display-address
      wallet> display-address 4 5 1

    """
    if not state.Wallet.quorum_m or not state.Wallet.pubkey_records:
        print_formatted_text(
            "Account map not previously set. Please use set-account-map first to set an account map that we can derive bitcoin addresses from"
        )
        return

    # Format params
    offset = int(offset)
    limit = int(limit)
    is_change = bool(is_change)
    testnet = state.Testnet

    to_print = f"{state.Wallet.quorum_m}-of-{len(state.Wallet.pubkey_records)} Multisig {'Change' if is_change else 'Receive'} Addresses"
    if not is_libsec_enabled():
        # TODO: use libsec bindings in buidl for 100x performance increase
        to_print += "\n(this is ~100x faster if you install libsec)"
    print_formatted_text(to_print + ":")
    generator = state.Wallet.derive_child_address(
        testnet=testnet, is_change=is_change, offset=offset, limit=limit
    )
    for cnt, address in enumerate(generator):
        print_formatted_text(f"#{cnt + offset}: {address}")


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
