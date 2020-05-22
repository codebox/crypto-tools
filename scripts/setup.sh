#!/usr/bin/env bash

ENV_DIR=env

function activate {
    source ${ENV_DIR}/bin/activate
}
if [ ! -d $ENV_DIR ]; then
    python3 -m venv $ENV_DIR
    activate
    pip install cryptography
    pip install flask
    pip install requests
else
    activate
fi
