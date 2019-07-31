# Testing Script

## SetUp

QRcodes are provided for the example below, they were generated with the
script at tests/fixtures/generate_fixture_images.py.


## Purge Hermit

To start from a clean install, remove any files that hermit looks for
or creates:

```
rm /tmp/wallet_words.json
rm /tmp/wallet_words.json.persisted
rm /tmp/wallet_words.json.backup
rm /etc/hermit.yaml
```

## Test Interface

Start it up:

```
source environment.sh
hermit
```

Check the help messages (repeat for other commands):

```
help
help debug
help export-xpub
```

Check that incorrect command call shows help:

```
export-pubkey
```

this should show the help message for export-pubkey.

### Test Shards Interface

```
shards
```

check the help messages for the shards commands


## Input Test shards


```
hermit
shards
intialize-shards-file
input-shard test1
2
1
test1
merge alley lucky axis penalty manage latin gasp virus captain wheel deal
input-shard test2
2
2
chase fragile chapter boss zero dirt stadium tooth physical valve kid plunge
test2
write-shards
persist-shards
backup-shards
```

### Test shard loading

TODO: shut off hermit, open and reload shards



### Test xpub and public key generation

For this example we are using BIP32 path `m/45'/1'/121'/20/26`.
Get back to the main hermit interface (`quit` from shards mode).

```
export-xpub m/45'/1'/121'/20/26
# unlock wallet with shards and passwords
# expected output:
# xpub6G9Qk16E4XtVVXBVPC3st2ndzdHn3tQyWH4ragyj4rL59qq2eL9QT5TXAmfvKQoCZD94kzHTGibJXU4ZBAA3V7PRuZXQopzVdczbepfVyCk

export-pubkey m/45'/1'/121'/20/26
# expected output:
# 026c76fc386b6c339577eea265242eb902df43155a0eaf23af1f96c5d9f2d10f63
```


## Generate Seed via Entropy generation



## Transaction Signing



Set testnet mode

```
testnet
```

take a picture of the example signing request qrcode located at
tests/fixtures/opensource_bitcoin_signature_request_0.jpg


```
sign-bitcoin
```

expected display:
```
ADDRESS:
2NAy762TReQqjNbNLdh3sK7cnje4GA4UfoW

INPUTS:
  ADDRESS 2NAy762TReQqjNbNLdh3sK7cnje4GA4UfoW	AMOUNT 0.26734591 BTC

OUTPUTS:
  ADDRESS 2NCcmVAirNBDTQYvecdDpKNJVdKJruwdUSZ	AMOUNT 0.12345678 BTC
  ADDRESS 2MyvsR5gizb6JHSECL6csBHwpW1wL8xqHp4	AMOUNT 0.14374378 BTC

FEE: 0.00014535 BTC

SIGNING AS: m/45'/1'/500'/200/26

Sign the above transaction? [y/N]
```



expected output:

```
Signature Data: 
{
  "pukey": "026c76fc386b6c339577eea265242eb902df43155a0eaf23af1f96c5d9f2d10f63",
  "signatures": [
    "30450221008b78f222bcdf18d03e12850c8600149769eebfed046b43dc9de5c5ab906f041c02206a2a75f94751fd3d2702ac1c3a4d563f40bc6911eebc40dfeed7d678522a1498",
    "30450221009f1fa6926a6a75b1f13867c57e645f67f709491646fc876e1ceefd219e1858dd022050f389540c4fda099431437bc669f3364f8d925a56778afcb4613b95772e6e9c",
    "304402206c1add9c084d22d28fa3e844d9b702a460bfadfc75843759657fc090417e05ce0220633e5468ca9d85440cf30099aa859651ec2eeedd8c68351b399f5e1577bf5754"
  ]
}
```