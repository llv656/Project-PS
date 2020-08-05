#!/bin/bash

export DJANGO_SETTINGS_MODULE=service_adminServ.settings

sleep 15

su -c 'python3 -u manage.py makemigrations' limitado
su -c 'python3 -u manage.py migrate' limitado
su -c 'python3 -u user_service.py' limitado
su -c 'gunicorn --bind :8080 service_adminServ.wsgi:application --reload' limitado
