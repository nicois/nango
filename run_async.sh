#!/bin/bash
set -ex
cd project
daphne project.asgi:application
