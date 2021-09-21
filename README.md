# LEGO [![Build Status](https://ci.webkom.dev/api/badges/webkom/lego/status.svg)](https://ci.webkom.dev/webkom/lego) [![Requirements Status](https://requires.io/github/webkom/lego/requirements.svg?branch=master)](https://requires.io/github/webkom/lego/requirements/?branch=master)

> Open source backend for abakus.no, frontend located at [webkom/lego-webapp](https://github.com/webkom/lego-webapp)

[![MIT](https://badgen.net/badge/license/MIT/blue)](https://en.wikipedia.org/wiki/MIT_License) [![last commit](https://badgen.net/github/last-commit/webkom/lego/)](https://github.com/webkom/lego/commits/master) [![contributors](https://badgen.net/github/contributors/webkom/lego)](https://github.com/webkom/lego/graphs/contributors)

> LEGO Er Ganske Oppdelt

## Getting started

LEGO requires `python3.7`, `python3.7-venv`, `docker` and `docker-compose`. Services like Postgres, Redis, Thumbor and Minio run inside docker.

```bash
# Initial setup (only need to once)
$ git clone git@github.com:webkom/lego.git && cd lego/
$ python3 -m venv venv
$ echo "from .development import *" > lego/settings/local.py
$ source venv/bin/activate
$ pip install -r requirements/dev.txt
$ docker-compose up -d
$ python manage.py initialize_development

# Activate and run (do every time)
$ docker-compose up -d
$ source venv/bin/activate
$ python manage.py runserver
```

> If you get problems it can be a solution to delete the `venv`, and do a fresh setup

## Code Style

This codebase uses the PEP 8 code style. We enforce this with isort, black & flake8.
In addition to the standards outlined in PEP 8, we have a few guidelines
(see `setup.cfg` for more info):

Format the code with black & isort

```bash
$ make fixme
```

To check if it is formatted properly, run:

```bash
$ tox -e isort -e flake8 -e black
```

## Tests

If you want to run a specific test class you can run

```bash
$ ./manage.py test lego.apps.[APP]
```

You can add flags to speed up the tests

> By adding the `--keepdb` the next time it will go a lot faster to run the tests multiple times.
> By adding the `--parallel` will run multiple tests in parallel using multiple cores.

If you want to check your test coverage, you can do the following

```bash
# Install the packages needed
$ pip install -r requirments/coverage.txt

# Run a full test run with coverage. This will run all tests in LEGO.
$ coverage run --source=lego ./manage.py test

# Then you can output the full coverage report
$ coverage report
# or a small one that only contains the things you are interested in
$ coverage report | grep [some string]
```

## Deployment

Lego runs in `Docker Swarm` and deploys are managed by `Drone` and `Ansible`.

How to deploy:

1.  Make sure the changes is pushed to master and the test passes.
2.  Have you added some new settings in `settings/`? If so make sure the `Ansible variables` reflects these changes.
3.  We run migrations automatically, make sure they work!
4.  Push to the `prod` branch. From master: `git push origin master:prod`
5.  Wait for the `prod` build to complete, last step will be `docker build`
6.  Go to [ci.webkom.dev](https://ci.webkom.dev/webkom/lego/) and use the deployment feature to deploy the production build.

Ansible will run the playbook for deploying the new build to `staging` or `production`.

<details><summary><code>Testing with elasticsearch</code></summary>

### Testing with elasticsearch

By default, development uses postgres for search. ~~We use elasticsearch in production~~, so you might want to test things locally with elasticsearch. In order to do so, you need to run elasticsearch from `docker-compose.extra.yml` by running `docker-compose -f docker-compose.extra.yml up -d`. Then you need to run lego with the env variable `SEARCH_BACKEND=elasticsearch`. You might need to run the migrate_search and rebuild_index commands to get elasticsearch up to date.

</details>

<details><summary><code>Debugging</code></summary>

### Debugging

If you get an error while installing requirements, you might be missing some dependencies on your system.

```bash
$ apt-get install libpq-dev python3-dev
```

> For MACOS you need to `brew install postgresql`

If you get an error while running initialize_development mentioning `elasticsearch`, you probably need run the following code, and then start over from `docker-compose up -d`. [Read why and how to make it permanent on Elasticsearch docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html).

```bash
$ sysctl -w vm.max_map_count=262144
```

If you get ld: library not found for -lssl

```
export LDFLAGS="-L/usr/local/opt/openssl/lib"
```

When changing the user fixtures one must load new fixtures

```
./manage.py load_fixtures --generate
```

An overview of the available users for development can be found in [this PR](https://github.com/webkom/lego/pull/1913)

</details>
