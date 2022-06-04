#!/bin/sh

flags=''
for arg in "$@"; do
  shift
  case "$arg" in
    "--sql") flags="$flags --print-sql";;
    *)       ;;
  esac
done

python manage.py runserver_plus $flags --keep-meta-shutdown
