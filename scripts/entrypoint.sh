#!/bin/sh

if [ "$DATABASE_ENGINE" = "postgresql" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

./scripts/setup.sh

exec "$@"
