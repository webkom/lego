# LEGO [![DroneCI](https://ci.abakus.no/api/badges/webkom/lego/status.svg?branch=master)](https://ci.abakus.no/webkom/lego)

> LEGO Er Ganske Oppdelt

LEGO is the backend for [abakus.no](https://abakus.no) - the frontend is located at
[webkom/lego-webapp](https://github.com/webkom/lego-webapp).
Documentation is located at [lego.abakus.no](https://lego.abakus.no). We also have a [beginner's guide for setting up LEGO](https://github.com/webkom/lego/wiki/Noob-Guide).

We use GitHub issues and project boards for simple project management.

## Getting started

LEGO requires `python3.7`, `virtualenv`, `docker` and `docker-compose`. Services like Postgres, Redis,
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

### Debugging

If you get an error while installing requirements, you might be missing some dependencies on your system.

```bash
$ apt-get install libpq-dev python3-dev
```

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

After changes

## Code Style

This codebase uses the PEP 8 code style. We enforce this with isort, black & flake8.
In addition to the standards outlined in PEP 8, we have a few guidelines
(see `setup.cfg` for more info):

Format the code with black & isort

```bash
$ isort -rc lego # Sort imports
$ black lego  # Format with black
```

To check if it is formatted properly, run:

```bash
$ tox -e isort -e flake8 -e black
```

### Tests

If you want to run a specific test class you can run

```bash
$ ./manage.py test lego.apps.[APP] --keepdb
```

By adding the `--keepdb` the next time it will go a lot faster to run the tests multiple times.

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

Lego runs in Kubernetes and deploys are managed by Drone and Spinnaker.

How to deploy:

1.  Make sure the changes is pushed to master and the test passes.
2.  Have you added some new settings in `settings/`? If so make sure the Spinnaker deployment reflects these changes.
3.  We run migrations automatically, make sure they work!
4.  Push to the `prod` branch. From master: `git push origin master:prod`

Spinnaker now starts the deployment. This takes some time, tests must pass and we have to build a
docker image.

## Tools

We recommend Pycharm for development, use your @stud.ntnu.no email to register a free professional
account.
