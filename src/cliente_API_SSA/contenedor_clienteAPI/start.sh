#!/bin/bash

export DJANGO_SETTINGS_MODULE=cliente_monitorAPI.settings

sleep 15

su -c 'python3 -u manage.py makemigrations' limitado
su -c 'python3 -u manage.py migrate' limitado
su -c 'python3 -u user_cliente.py' limitado
su -c 'gunicorn --bind :8080 cliente_monitorAPI.wsgi:application --reload' limitado

