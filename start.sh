#!/bin/sh

SESSION_NAME="jailman"
PYTHON=$(which python3.11)

# check if the screen session already exists
if screen -list | grep -q "[.]${SESSION_NAME}[[:space:]]"; then
    echo "Screen session '$SESSION_NAME' already running."
    exit 1
fi

# create virtual environment
${PYTHON} -m venv .venv
. .venv/bin/activate

# install requirements
pip install -r requirements.txt

# start in a detached screen session
screen -dmS "$SESSION_NAME" ./jailman.py
echo "Started '$SESSION_NAME' in detached screen session."

# how to attach later:
# screen -r jailman

