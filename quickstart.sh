#!/bin/bash
set -xeuo pipefail

# Create a fresh python virtualenv in /tmp/
VENV_DIR="nango-quickstart-virtualenv"
python3 -m venv "$VENV_DIR"
.  "${VENV_DIR}/bin/activate"

pip install -r requirements.txt
cd project
[[ -e db.sqlite3 ]] || cp db.sqlite3.template db.sqlite3
./manage.py migrate
./manage.py runserver
