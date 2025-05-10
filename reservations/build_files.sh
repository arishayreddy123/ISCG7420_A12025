#!/usr/bin/env bash
set -e

# 1) install dependencies
pip install -r requirements.txt

# 2) apply migrations
python manage.py migrate --noinput

# 3) collect static into STATIC_ROOT
python manage.py collectstatic --noinput --clear
