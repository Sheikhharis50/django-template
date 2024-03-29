# django-template

> [Sheikh Haris Zahid](https://github.com/Sheikhharis50)

Template for django to boost the project creation. Please Fork before using it, Thanks.

## Features
- Poetry for Dependcies managment.
- Environments setup for Develop and Production.
- DjangoRestFramework attached.
- By Default, all APIs related to authentication is provided using SimpleJWT package.
- Mail Sending Utility. (Async)
- Notification Sending Utility. (Sync)
- Job Scheduling scripts.
- Custom Permissions.
- AWS S3 support. 
- Dockerized.

## Usage
1) Install [Poetry](https://python-poetry.org/docs/)
2) Create & Setup Enviornment:
```
poetry shell
poetry install
```
3) To run with SQL:
```
./scripts/runserver.sh --sql
```
4) To run Shell with SQL:
```
./scripts/shell.sh --sql
```
5) In order to run in production:
```
# build containers and run as detached
docker-compose up -build -d
# create superuser
docker-compose exec web python manage.py createsuperuser
```
