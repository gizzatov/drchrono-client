[![CircleCI](https://circleci.com/gh/gizzatov/drchrono-client.svg?style=svg)](https://circleci.com/gh/gizzatov/drchrono-client)

# About
This is a simple implementation of web-client example for drchrono based on Django.

# How to run project
```
docker-compose build
docker-compose up
```
Then you can open a localhost page with 3000 port in your web browser:

`http://localhost:3000/`

# Environment variables:
* `DJANGO_SETTINGS_MODULE` - string with path to django settings file(example: application.settings.local_dev)
* `PG_USER` - Postgres user
* `PG_PASSWORD` - Postgres password
* `PG_HOST` - Postgres host
* `PG_PORT` - Postgres port
* `PG_DB` - database name
* `REDIS_HOST` - Redis host
* `REDIS_PORT` - Redis port (default: 6379)
* `SOCIAL_AUTH_DRCHRONO_KEY` - drchrono OAuth key
* `SOCIAL_AUTH_DRCHRONO_SECRET` - drchrono OAuth secret
