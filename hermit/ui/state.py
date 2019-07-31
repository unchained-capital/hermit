from os import environ

from hermit.wallet import HDWallet

Timeout = 0


Live = False

Debug = 'DEBUG' in environ
Testnet = 'TESTNET' in environ

Wallet = HDWallet()

Session = None
