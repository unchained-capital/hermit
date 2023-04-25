#
# This script sets up the local shell environment.
#

#
# Do NOT run this script (`./environment.sh` or `bash
# environment.sh`); instead source it (`source environment.sh`).
#
SCRIPT_NAME=$(basename "${0/-/}")
SOURCE_NAME=$(basename "$BASH_SOURCE")
if [ "$SCRIPT_NAME" = "$SOURCE_NAME" ]; then
    echo "ERROR: Do not execute ('bash environment.sh') this script! Source it instead ('source environment.sh')" >&2
    exit 1
fi

#
# Directories
#
ROOT_DIR=$(pwd)
LIB_DIR="${ROOT_DIR}"
BIN_DIR="${ROOT_DIR}/bin"

#
# Python virtualenv
#

VENV_NAME=".virtualenv"
VENV_DIR="${ROOT_DIR}/${VENV_NAME}"
if [ -d "$VENV_DIR" ]; then
    . "${VENV_DIR}/bin/activate"
else
    echo "ERROR: Python virtualenv directory (${VENV_DIR}) does not exist.  Did you run 'make' yet?" >&2
    exit 2
fi

#
# PYTHONPATH
#
# We need to add this application's 'lib' dir to PYTHONPATH.
#

if [ -z $(echo "$PYTHONPATH" | grep "$LIB_DIR") ]; then
    export PYTHONPATH="${PYTHONPATH}:${LIB_DIR}"
fi

#
# PATH
#
# We need to add this application's 'bin' dir to PATH.
#

if [ -z $(echo "$PATH" | grep "$BIN_DIR") ]; then
    export PATH="${BIN_DIR}:${PATH}"
fi
