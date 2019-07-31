import os

with open(os.path.join(os.path.dirname(__file__), "shard.txt"), "r") as f:
    ShardWords = [word.strip() for word in f]
with open(os.path.join(os.path.dirname(__file__), "wallet.txt"), "r") as f:
    WalletWords = [word.strip() for word in f]
