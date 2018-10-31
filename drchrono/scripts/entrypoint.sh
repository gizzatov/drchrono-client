#!/usr/bin/env bash

python manage.py collectstatic --noinput
uwsgi --ini /app/uwsgi.ini
