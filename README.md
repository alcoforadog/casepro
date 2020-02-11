# CasePro

![Build Status](https://travis-ci.org/rapidpro/casepro.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/github/rapidpro/casepro/badge.svg?branch=master)](https://coveralls.io/github/rapidpro/casepro?branch=master)

Case management dashboard for UNICEF and partner organizations. Supports use of both [RapidPro](http://rapidpro.io) and [Junebug](https://github.com/praekelt/junebug) as messaging backends.

For documentation see the [project wiki](https://github.com/rapidpro/casepro/wiki) which includes essential 
information for both developers and administrators.

## Docker development environment

**Install**
To install docker and docker compose on you machine folow the links below

* [Docker](https://docs.docker.com/install/)
* [Docker Compose](https://docs.docker.com/compose/install/)

To init the development environment with docker run:

```bash
docker-compose up
```

**Database**
You can access the database with the follow auth

```text
Host: localhost
Port: 5431
Database: casepro
Username: casepro
Password: nyaruka
```

**Login**
To create a new super user you can run commant below

```bash
docker exec -it casepro_app_1 python manage.py createsuperuser
```

Obs: confirm the container name before run this command;