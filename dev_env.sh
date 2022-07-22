#!/bin/sh

export SECRET_KEY="ni^!n2d#!)(3bgt)_3#w)fwa-f_!w!_ularz=nov_*lu!%t4l3"
export DEBUG=1
export DJANGO_SUPERUSER_EMAIL=admin@admin.com
export DJANGO_SUPERUSER_USERNAME=django_user
export DJANGO_SUPERUSER_PASSWORD=django_pass
export POSTGRES_USER=gis_user
export POSTGRES_PASSWORD=gis_pass
export POSTGRES_DB=gis_db

source venv/bin/activate