from sys import argv
from os.path import basename
import string
import random

# python scripts/generate_large_bitcoin_request.py > tests/fixtures/large_bitcoin_signature_request.json 

def generate_large_bitcoin_request(N):
    header = """{

    "bip32_path": "m/45'/1'/120'/20/26",

    "inputs": [
      [
        "522102a567420d0ecb8ae1ac3794a6f901c9fdfa63a24476b8889d4c483dc7975f4ab321034a7496c358ee925043f5859bf7a191566fa070e3b75aac3f3bde6a670a8b6a8e2103666946ad4ff2b8c5c1ed6c8f5dd7f28769820cf35061ad5e02a45c5f05d54a1853ae","""

    footer = """
      ]
    ],

    "outputs": [
        {
            "address": "2NG4oZZZbBcBtUw6bv2KEJmbZgrdLTTf5CC",
            "amount": 10000000
        },
        {
            "address": "2MuK9EGZeXMLJTqVtv8eKrcbrvYg2pwD1te",
            "amount": 27002781
        }
    ]

}"""
    tmp1 = """
        {
            "txid": \""""
    tmp2 = """\",
            "n": 0,
            "amount": """
    tmp3 = """
        }"""
    input_array = [(tmp1
                    + ''.join([random.choice(string.hexdigits[:16]) for x in range(64)])
                    + tmp2
                    + ''.join([random.choice(string.digits[1:]) for x in range(7)])
                    + tmp3) for x in range(N)]
    input_array = ','.join(input_array)
    print(header + input_array + footer)

if __name__  == '__main__':
    if len(argv) < 2:
        print("usage: {} NUM_INPUTS".format(basename(__file__)))
        exit(1)
    generate_large_bitcoin_request(int(argv[1]))
