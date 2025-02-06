# LEGO

> Open source backend for abakus.no, frontend located at [webkom/lego-webapp](https://github.com/webkom/lego-webapp)

[![MIT](https://badgen.net/badge/license/MIT/blue)](https://en.wikipedia.org/wiki/MIT_License)
[![last commit](https://badgen.net/github/last-commit/webkom/lego/)](https://github.com/webkom/lego/commits/master)
[![contributors](https://badgen.net/github/contributors/webkom/lego)](https://github.com/webkom/lego/graphs/contributors)
[![Build Status](https://ci.webkom.dev/api/badges/webkom/lego/status.svg)](https://ci.webkom.dev/webkom/lego)
[![codecov](https://codecov.io/gh/webkom/lego/branch/master/graph/badge.svg?token=4JI1CMu58M)](https://codecov.io/gh/webkom/lego)

> LEGO Er Ganske Oppdelt

## Getting started

LEGO requires `python3.11`, `python3.11-venv`, `docker` and `poetry`. Services like Postgres, Redis, Thumbor and Minio run inside docker.

### Initial setup (only needed once)

```bash
$ git clone git@github.com:webkom/lego.git && cd lego/
$ python3.11 -m venv .venv
$ echo "from .development import *" > lego/settings/local.py
$ source .venv/bin/activate
$ poetry install
$ docker compose up -d
$ python manage.py initialize_development
```

### Activate and run (every time)

```bash
$ source .venv/bin/activate
$ docker compose up -d
$ python manage.py runserver
```

#### Notes

```bash
# Note 1: Whenever you switch branches you might need to make minor changes

$ poetry install # If the branch has changes in the dependencies
$ python manage.py migrate # If the branch has a database in another state than yours

# Note 2: When you make changes to models, or constants used by models, you need to create new migrations

$ python manage.py makemigrations # Creates one or more new files that must be commited

# Remember to format generated migrations! (using e.g. `make fixme`)
```

**`poetry.lock` conflicts**

If you have updated dependencies it's likely you might get conflicts in the Poetry lock file.
This solution should resolve most conflicts quite well:

```bash
$ git rebase origin/master

# If conflicts
$ git checkout --theirs poetry.lock

$ poetry lock --no-update

# The conflicts should be resolved
```

> If you get problems it can be a solution to delete the `.venv`, and do a fresh setup

## Code Style

This codebase uses the PEP 8 code style. We enforce this with `isort`, `black` & `flake8`. In addition to the standards outlined in PEP 8, we have a few guidelines (see `pyproject.toml` for more info):

Format the code with `isort` & `black`

```bash
$ make fixme
```

To check if it is formatted properly, run:

```bash
$ tox -e isort -e black -e flake8
```

To check if it is typed properly, run:

```bash
$ tox -e mypy
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
# Run all tests in LEGO. Remember to add the recommended flags mentioned above
$ tox -e tests --
# or run without tox
$ coverage run --source=lego ./manage.py test

# If you now have multiple coverage files or a .coverage.* file, you'll have to combine it in order to output report
$ coverage combine

# Then you can output the full coverage report
$ coverage report
# or a small one that only contains the things you are interested in
$ coverage report | grep [some string]
```

## Deployment

LEGO runs in `Docker Swarm` and deploys are managed by `Drone` and `Ansible`.

How to deploy:

1.  Make sure the changes are pushed to master and the test passes.
2.  Have you added some new settings in `settings/`? If so, make sure the `Ansible variables` reflects these changes.
3.  We run migrations automatically, make sure they work!
4.  Push to the `build` branch. From master: `git push origin master:build`
5.  Wait for the `build` build to complete. The last step will be `docker build`
6.  Go to [ci.webkom.dev](https://ci.webkom.dev/webkom/lego/) and use the promote feature to deploy the staging/production build.

Ansible will automatically run the playbook for deploying the new build to `staging` or `production` based on the target selected in step 6.

<details><summary><code>Testing with elasticsearch</code></summary>

### Testing with elasticsearch

By default, development and production uses postgres for search. We can still enable elasticsearch backend in prod, so you can test things locally with elasticsearch. In order to do so, you need to run elasticsearch from `docker-compose.extra.yml` by running `docker-compose -f docker-compose.extra.yml up -d`. Then you need to run lego with the env variable `SEARCH_BACKEND=elasticsearch`. You might need to run the migrate_search and rebuild_index commands to get elasticsearch up to date.

</details>

<details><summary><code>Debugging</code></summary>

### Debugging

If you get an error while installing project dependencies, you might be missing some on your system.

```bash
$ apt-get install libpq-dev python3-dev
```

> For MACOS you need to `brew install postgresql`

If you get an error while running initialize_development mentioning `elasticsearch`, you probably need to run the following code, and then start over from `docker-compose up -d`. [Read why and how to make it permanent on Elasticsearch docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html).

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
