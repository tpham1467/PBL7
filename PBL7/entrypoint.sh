#!/bin/ash

echo "Apply database migrations"
python manage.py migrate

echo "starting celery monitor"
celery -A PBL7 flower --port=5000
# celery --broker=redis://redis@localhost:6379/0 flower

exec "$@"