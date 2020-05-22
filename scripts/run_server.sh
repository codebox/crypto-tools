#!/usr/bin/env bash
. scripts/setup.sh
export FLASK_APP=server/web.py
#export FLASK_ENV=development
flask run