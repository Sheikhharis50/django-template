#!/bin/sh

flags=''
for arg in "$@"; do
  shift
  case "$arg" in
    "--sql") flags="$flags --print-sql";;
    *)       ;;
  esac
done

python manage.py shell_plus $flags
