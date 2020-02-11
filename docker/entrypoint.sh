#!/bin/bash
python /usr/src/app/manage.py migrate
python /usr/src/app/manage.py runserver 0.0.0.0:8000

celery worker -A casepro -Q celery -B -n casepro.celery --loglevel=INFO
celery worker -A casepro -Q sync -n casepro.sync --loglevel=INFO