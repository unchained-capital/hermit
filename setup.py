import setuptools
import os

import sys
if sys.version_info < (3,7):
    sys.exit('Sorry, Python < 3.7 is not supported')
    
def __path(filename):
    return os.path.join(os.path.dirname(__file__),
                        filename)

if os.path.exists(__path('build.info')):
    build = open(__path('build.info')).read().strip()

version = '0.1.3'

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hermit",
    version=version,
    author="Unchained Capital Engineering",
    author_email="engineering@unchained-capital.com",
    description="Unchained Capital Hermit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/unchained-captial/hermit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    scripts=[
        'bin/hermit'
    ],
    install_requires=[
        'pyzbar>=0.1.7',
        'bson>=0.5.8',
        'opencv-python>=3.4.3',
        'imutils>=0.5',
        'qrcode[pil]>=6',
        'prompt-toolkit>=2.0.7',
        'pyAesCrypt>=0.4.2',
        'mnemonic>=0.18',
        'python-bitcoinlib>=0.10',
        'pytest>=4',
        'ecdsa>=0.13',
        'pysha3>=1',
        'eth-account>=0.3',
        'pyyaml>=3.13',
        'shamir_mnemonic==0.1',
    ],
    data_files=[
        ('pybitcointools', ['pybitcointools/english.txt']),
        ('hermit', ['hermit/wordlists/shard.txt', 'hermit/wordlists/wallet.txt']),
    ],
    include_package_data=True,
)
