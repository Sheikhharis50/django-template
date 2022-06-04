#!/bin/sh

echo "Running migrations..."
python manage.py migrate

echo "Seeding..."
fixtures=$(ls seed/)
for f in $fixtures; do
    echo "Seeding $f"
    python manage.py loaddata seed/$f
done
