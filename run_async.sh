#!/bin/bash
set -ex
cd project
./manage.py collectstatic --no-input
daphne  project.asgi:application
