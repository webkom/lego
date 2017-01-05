FROM python:3.6
MAINTAINER Abakus Webkom <webkom@abakus.no>

ENV PYTHONPATH /app/
ENV PYTHONUNBUFFERED 1

ENV ENV_CONFIG 1

ENV CASS_DRIVER_NO_CYTHON 1
ENV CASS_DRIVER_NO_EXTENSIONS 1

RUN mkdir -p /app
COPY . /app/
WORKDIR /app

RUN set -e \
    && apt-get update \
    && apt-get install -y git \
    && apt-get autoremove -y \
    && apt-get clean \
    && pip install --no-cache -r requirements/prod.txt \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN set -e \
    && echo 'SECRET_KEY="secret"' > lego/settings/local.py \
    && ENV_CONFIG=0 python manage.py collectstatic --noinput
