#!/bin/bash

sleep 15

su -c 'python3 -u manage.py makemigrations' limitado
su -c 'python3 -u manage.py migrate' limitado
su -c 'gunicorn --bind 0.0.0.0:8080 adminServ.wsgi:application --reload' limitado
