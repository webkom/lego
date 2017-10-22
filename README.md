# LEGO [![CircleCI](https://circleci.com/gh/webkom/lego/tree/master.svg?style=svg&circle-token=26520c314e094786c87c6a14af78c0cd7c82caec)](https://circleci.com/gh/webkom/lego/tree/master)

> LEGO Er Ganske Oppdelt

LEGO is the backend for [abakus.no](https://abakus.no) - the frontend is located at
[webkom/lego-webapp](https://github.com/webkom/lego-webapp).
Documentation is located at [lego.abakus.no](https://lego.abakus.no). We also have a [beginner's guide for setting up LEGO](https://github.com/webkom/lego/wiki/Noob-Guide).

We use GitHub issues and project boards for simple project management.

## Getting started

LEGO requires python3.6, virtualenv, docker and docker-compose. Services like Postgres, Redis,
Elasticsearch, Thumbor and Minio run inside docker.


```bash
$ git clone git@github.com:webkom/lego.git && cd lego/
$ python3 -m venv venv
$ source venv/bin/activate
$ echo "from .development import *" > lego/settings/local.py
$ pip install -r requirements/dev.txt
$ docker-compose up -d
$ python manage.py initialize_development
$ python manage.py runserver
```

## Code Style

This codebase uses the PEP8 code style. We enforces this with flake8. We use almost all the rules
used in the Requests project.

In addition to the standards outlined in PEP 8, we have a few guidelines:

* Line-length can exceed 79 characters, to 100, when convenient.
* Always use single-quoted strings (e.g. 'lego'), unless a single-quote occurs within the string.

Additionally, one of the styles that PEP8 recommends for line continuations completely lacks all
sense of taste, and is not to be permitted within the Requests codebase:

```
# Aligned with opening delimiter. WRONG
foo = long_function_name(var_one, var_two,
                         var_three, var_four)

# Correct
foo = long_function_name(
    var_one, var_two, var_three, var_four
)
foo = long_function_name(
    var_one,
    var_two
)
```

## Deployment

Lego runs in Kubernetes and deploys are managed by Drone and Spinnaker.

How to deploy:
1. Make sure the changes is pushed to master and the test passes.
2. Have you added some new settings in `settings/`? If so make sure the Spinnaker deployment reflects these changes.
3. We run migrations automatically, make sure they work!
4. Push to the `prod` branch. From master: `git push origin master:prod`

Spinnaker now starts the deployment. This takes some time, tests must pass and we have to build a
docker image.

## Tools

We recommend Pycharm for development, use your @stud.ntnu.no email to register a free professional
account.
