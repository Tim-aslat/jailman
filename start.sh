#!/bin/sh

# check if python exists
PYTHON=`which python`

# create the virtual environment for any additional modules that may be required
${PYTHON} -m venv .venv
. .venv/bin/activate

./jailman.py
