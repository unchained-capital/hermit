#
# == Environment ==
#

UNAME := $(shell uname)

#
# == Files & Directories ==
#

PYTHON_REQUIREMENTS := requirements.in
PYTHON_FROZEN_REQUIREMENTS := requirements.txt

VENV_DIR := .virtualenv
FIXTURES := tests/fixtures
SCRIPTS := scripts
EXAMPLES := examples

#
# == Commands ==
#

CAT := cat
ECHO := echo

BREW := brew
APT := apt

SYSTEM_PYTHON3 := $(shell command -v python3 2> /dev/null)
PYTHON3 := $(VENV_DIR)/bin/python3
PIP := $(VENV_DIR)/bin/pip

PYTEST := $(VENV_DIR)/bin/pytest
BLACK := $(VENV_DIR)/bin/black
FLAKE8 := $(VENV_DIR)/bin/flake8
MYPY := $(VENV_DIR)/bin/mypy
SPHINX_BUILD := $(VENV_DIR)/bin/sphinx-build
TWINE := twine

default: dependencies

#
# == Dependencies ==
#

freeze:
	$(PIP) freeze -l > $(PYTHON_FROZEN_REQUIREMENTS)

dependencies: system-dependencies python-dependencies

system-dependencies:
ifeq ($(UNAME),Darwin)
	$(BREW) ls --versions zbar || brew install zbar
else
	$(APT) install libzbar0
endif

python-dependencies: $(VENV_DIR)
	$(PYTHON3) -m pip install --upgrade pip
	$(PIP) install wheel
ifdef UNFREEZE
	 $(PIP) install -r $(PYTHON_REQUIREMENTS)
else
	$(PIP) install -r $(PYTHON_FROZEN_REQUIREMENTS)
endif


$(VENV_DIR):
	$(SYSTEM_PYTHON3) -m venv --prompt='hermit' $(VENV_DIR)

#
# == Development ==
#

check:
	$(BLACK) --check hermit tests scripts *.py
	$(FLAKE8) hermit tests scripts *.py
	$(MYPY) -p hermit

test:
	$(PYTEST) --cov=hermit --cov-config=tests/.coveragerc --ignore=vendor

docs:
	HERMIT_LOAD_ALL_IO=true $(SPHINX_BUILD) -c docs hermit docs/_build

#
# == Examples & Fixtures ==
#

fixtures: $(FIXTURES)/signature_requests/2-of-2.p2sh.testnet.coordinator_signed.gif $(FIXTURES)/signature_requests/2-of-2.p2sh.testnet.gif $(EXAMPLES)/lorem_ipsum.gif $(EXAMPLES)/hello_world.jpg

$(EXAMPLES)/lorem_ipsum.gif: $(FIXTURES)/lorem_ipsum.txt
	$(CAT) $< | $(PYTHON3) $(SCRIPTS)/create_qr_code_animation.py $@

$(EXAMPLES)/hello_world.jpg: $(FIXTURES)/hello_world.txt
	$(CAT) $< | $(PYTHON3) scripts/create_qr_code_image.py $@

%.gif: %.psbt
	$(CAT) $< | $(PYTHON3) $(SCRIPTS)/create_qr_code_animation.py $@ true

%.coordinator_signed.psbt: %.psbt
	$(CAT) $< | $(PYTHON3) $(SCRIPTS)/sign_psbt_as_coordinator.py $(FIXTURES)/coordinator.pem > $@


#
# == Release ==
#

build.info:
	$(ECHO) ${BUILD_NUMBER} > build.info

package: python-dependencies build.info
	$(PYTHON3) setup.py sdist bdist_wheel

release: package
	#$(TWINE) upload -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} --repository-url https://test.pypi.org/legacy/ dist/*
	$(TWINE) upload dist/*

.PHONY: docs

#
# == Cleanup ==
#

clean:
	$(RM) -rf docs/_build/* build/* dist/* hermit.egg-info build.info /tmp/shard_words.bson*

purge:
	$(RM) -rf $(VENV_DIR)
