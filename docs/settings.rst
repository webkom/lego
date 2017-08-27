Settings
========

Lego settings
-------------
Lego has a few settings. The defaults is placed in lego/settings/lego.py.

- SITE: Default project owner settings.
- API_VERSION: Current api version used by default.
- LOGIN_REDIRECT_URL: The redirect after a login. This is by default the api root.

Production settings
-------------------
Production reads configuration values form ENV variables.

Docker
------
We use Docker in production and manages our services with Kubernetes. The Docker image in not
currently public available, but you can build and distribute it by yourself.

::

    git clone git@github.com:webkom/lego.git
    cd lego
    docker build . -t webkom/lego:latest

Services
--------

Lego consists of many services, each with different responsibilities and scaling possibilities.

+------------------+-------------------------------------------+--------------------+
| Service          | Command                                   | Multiple instances |
+==================+===========================================+====================+
| API server       | uwsgi --ini lego.ini                      | Yes                |
+------------------+-------------------------------------------+--------------------+
| Celery Beat      | celery -A lego beat                       | No                 |
+------------------+-------------------------------------------+--------------------+
| Celery Worker    | celery -A lego worker                     | Yes                |
+------------------+-------------------------------------------+--------------------+
| Restricted Mail  | python manage.py restricted_email         | Yes                |
+------------------+-------------------------------------------+--------------------+
| Websocket Server | daphne lego.asgi:channel_layer -b 0.0.0.0 | Yes                |
+------------------+-------------------------------------------+--------------------+
| Websocket Worker | python manage.py runworker                | Yes                |
+------------------+-------------------------------------------+--------------------+

Lego also depends on multiple external services:

* Postgres - Database
* Redis - Cache, Celery broker and Websocket queue
* Elasticsearch - Search backend
* S3 / Minio - Filestorage
* Thumbor - Image resizer
* Cassandra - Feed backend
* LDAP (Optional) - Sync users to an external system
* Google GSuite (Optional) - Email provider
