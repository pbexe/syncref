#!/bin/sh
# wait-for-postgres.sh

set -e

host="$1"
shift

until psql -h "$host" -p 5432 -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

python manage.py collectstatic --no-input --clear 
python manage.py migrate
uvicorn syncref.asgi:application --workers 2 --host 0.0.0.0 --port 8000 --reload
