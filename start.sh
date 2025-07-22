#!/bin/sh

# check if python exists
PYTHON=`which python3.11`

# create the virtual environment for any additional modules that may be required
${PYTHON} -m venv .venv
. .venv/bin/activate

# install required modules
pip install -r requirements.txt

# run server
./jailman.py
