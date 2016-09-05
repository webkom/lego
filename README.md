# LEGO [![Build status](https://ci.frigg.io/badges/webkom/lego/)](https://ci.frigg.io/webkom/lego/last/) [![Coverage status](https://ci.frigg.io/badges/coverage/webkom/lego/)](https://ci.frigg.io/webkom/lego/last/)

> LEGO Er Ganske Oppdelt

We use [Waffle](https://waffle.io/webkom/lego) for simple project management.

[Noob guide for setting up LEGO](https://github.com/webkom/lego/wiki/Noob-Guide)

## Getting started

LEGO requires python3, virtualenv, docker and docker-compose. Services like Postgres, Redis and
Elasticsearch runs in docker.


```bash
    git clone git@github.com:webkom/lego.git && cd lego/
    virtualenv venv -p python3
    source venv/bin/activate
    docker-compose up
    python manage.py migrate
    python manage.py runserver
```

We recommend Pycharm for development, use your @stud.ntnu.no email to register a free professional
account.

