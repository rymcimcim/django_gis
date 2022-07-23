#!/bin/sh

export SECRET_KEY=# secret key
export DEBUG=# 0 or 1
export DJANGO_SUPERUSER_EMAIL=# admin email
export DJANGO_SUPERUSER_USERNAME=# admin username
export DJANGO_SUPERUSER_PASSWORD=# admin password
export POSTGRES_USER=# postgis username
export POSTGRES_PASSWORD=# postgis password
export POSTGRES_DB=# postgis database name

source venv/bin/activate