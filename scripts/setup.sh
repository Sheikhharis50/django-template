#!/bin/sh

echo "Making migrations...."
python manage.py makemigrations

echo "Running migrations...."
python manage.py migrate

echo "Collecting static data...."
python manage.py collectstatic
