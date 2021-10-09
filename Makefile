#
# == Paths & Directories ==
#

VENV_DIR := .virtualenv

PYTHON3                    := $(shell command -v python3 2> /dev/null)
PYTHON_REQUIREMENTS        := requirements.in
PYTHON_FROZEN_REQUIREMENTS := requirements.txt

#
# == Configuration ==
#

UNAME := $(shell uname)

#
# == Commands ==
#

PIP        := $(VENV_DIR)/bin/pip
PYTEST     := $(VENV_DIR)/bin/pytest
BLACK      := $(VENV_DIR)/bin/black
MYPY       := $(VENV_DIR)/bin/mypy
SPHINX_BUILD := $(VENV_DIR)/bin/sphinx-build

#
# == Targets ==
#

default: dependencies

docs:
	$(SPHINX_BUILD) -c docs hermit docs/_build

assets:
	echo 'Hello, world!' | python scripts/create_qr_code_image.py tests/fixtures/hello_world.jpg
	cat tests/fixtures/lorem.txt | $(PYTHON3) scripts/create_qr_code_animation.py examples/lorem.gif
	cat tests/fixtures/signature_requests/2-of-2.p2sh.testnet.psbt | $(PYTHON3) scripts/create_qr_code_animation.py tests/fixtures/signature_requests/2-of-2.p2sh.testnet.gif true
	cat tests/fixtures/signature_requests/2-of-2.p2sh.testnet.psbt | python scripts/sign_psbt_as_coordinator.py tests/fixtures/coordinator.pem  > tests/fixtures/signature_requests/2-of-2.p2sh.testnet.coordinator_signed.psbt
	cat tests/fixtures/signature_requests/2-of-2.p2sh.testnet.coordinator_signed.psbt | python scripts/create_qr_code_animation.py tests/fixtures/signature_requests/2-of-2.p2sh.testnet.coordinator_signed.gif true

clean:
	$(RM) -rf docs/_build/* build/* dist/* hermit.egg-info build.info $(VENV_DIR) /tmp/shard_words.bson*

freeze:
	$(PIP) freeze -l > $(PYTHON_FROZEN_REQUIREMENTS)

dependencies: system-dependencies python-dependencies

system-dependencies:
ifeq ($(UNAME),Darwin)
	brew ls --versions zbar || brew install zbar
else
	sudo apt install libzbar0
endif

python-dependencies: $(VENV_DIR)
	$(PIP) install wheel
ifdef UNFREEZE
	 $(PIP) install -r $(PYTHON_REQUIREMENTS)
else
	$(PIP) install -r $(PYTHON_FROZEN_REQUIREMENTS)
endif


build.info:
	echo ${BUILD_NUMBER} > build.info

package: python-dependencies build.info
	python setup.py sdist bdist_wheel

upload: python-dependencies package
	#twine upload -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} --repository-url https://test.pypi.org/legacy/ dist/*
	twine upload dist/*

$(VENV_DIR):
	$(PYTHON3) -m venv --prompt='hermit' $(VENV_DIR)

test:
	$(PYTEST) --cov=hermit --cov-config=tests/.coveragerc --ignore=vendor

lint:
	$(BLACK) --check hermit tests scripts
	$(MYPY) hermit/

.PHONY: test docs
