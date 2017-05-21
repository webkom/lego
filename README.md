# LEGO [![CircleCI](https://circleci.com/gh/webkom/lego/tree/master.svg?style=svg&circle-token=26520c314e094786c87c6a14af78c0cd7c82caec)](https://circleci.com/gh/webkom/lego/tree/master)

> LEGO Er Ganske Oppdelt

We use GitHub issues and project boards for simple project management.

Documentation is located inside the docs/ folder in this repository. We also have a [Noob guide for setting up LEGO](https://github.com/webkom/lego/wiki/Noob-Guide)

## Getting started

LEGO requires python3.6, virtualenv, docker and docker-compose. Services like Postgres, Redis,
Elasticsearch, Thumbor and Minio runs inside docker.


```bash
    git clone git@github.com:webkom/lego.git && cd lego/
    python3 -m venv venv
    source venv/bin/activate
    echo "from .development import *" > lego/settings/local.py
    pip install -r requirements/dev.txt
    docker-compose up -d
    python manage.py migrate
    python manage.py load_fixtures
    python manage.py runserver
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

No. Just don't. Please.

- Kenneth Reitz - Creator of the Requests project

## Deployment

Lego runs in Kubernetes and deploys are managed by Helm, Drone and Whale. The Helm Chart is located in the [charts repo](https://github.com/webkom/charts).
  
How to deploy:
1. Make sure the changes is pushed to master and the test passes.
2. Have you added some new settings in `settings/`? If so make sure the Helm chart reflects this and values in Whale are up to date.
3. We run migrations automatically, make sure they work! 
4. Push to the `prod` branch. From master: `git push origin master:prod`

Whale now starts the deployment. This takes some time, tests must pass and we have to build a 
docker image.

## Tools

We recommend Pycharm for development, use your @stud.ntnu.no email to register a free professional
account.

