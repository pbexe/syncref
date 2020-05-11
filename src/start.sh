#!/bin/sh

set -e

host="$1"
shift

until psql -h "$host" -p 5432 -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing commands"

python manage.py migrate
python manage.py createsuperuser --no-input --username $USERNAME_FIELD --email $EMAIL_FIELD
uvicorn syncref.asgi:application --workers 2 --host 0.0.0.0 --port 8000
