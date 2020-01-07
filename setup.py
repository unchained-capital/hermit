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

version = '0.1.11'

with open("README.md", "r") as fh:
    long_description = fh.read()

requirementPath = __path('requirements.frozen.txt')
install_requires = [] 
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

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
    install_requires=install_requires,
    data_files=[
        ('pybitcointools', ['pybitcointools/english.txt']),
        ('hermit', ['hermit/wordlists/shard.txt', 'hermit/wordlists/wallet.txt']),
    ],
    include_package_data=True,
)
