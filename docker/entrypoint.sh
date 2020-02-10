#!/bin/bash
python /usr/src/app/manage.py migrate
python /usr/src/app/manage.py runserver 0.0.0.0:8000