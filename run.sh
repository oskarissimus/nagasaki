#!/bin/bash
set -e #https://stackoverflow.com/questions/2870992/automatic-exit-from-bash-shell-script-on-error
alembic upgrade head
python nagasaki/trader/main.py
