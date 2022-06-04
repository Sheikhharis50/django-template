#!/bin/sh

echo "Running migrations..."
python manage.py migrate
