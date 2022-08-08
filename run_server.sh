#!/usr/bin/env bash

APPS_LIST=(
    "mixins"
    "users"
    "profiles"
    "resources"
    "projects"
    "experiments"
    "operations"
)

FIXTURES_LIST=(
  "aerpaw_roles"
)

#APPS_LIST=()

for app in "${APPS_LIST[@]}";do
    python manage.py makemigrations $app
done
python manage.py makemigrations
python manage.py showmigrations
python manage.py migrate

for fixture in "${FIXTURES_LIST[@]}";do
    python manage.py loaddata $fixture
done
python manage.py collectstatic --noinput

# development server
python manage.py runserver

# uwsgi server
#if [[ "${USE_DOT_VENV}" -eq 1 ]]; then
#    uwsgi --uid ${UWSGI_UID:-1000} --gid ${UWSGI_GID:-1000}  --virtualenv ./.venv --ini portal.ini
#else
#    uwsgi --uid ${UWSGI_UID:-1000} --gid ${UWSGI_GID:-1000}  --virtualenv ./venv --ini portal.ini
#fi