FROM python:3.6
MAINTAINER Abakus Webkom <webkom@abakus.no>

ARG RELEASE

ENV PYTHONPATH /app/
ENV PYTHONUNBUFFERED 1

ENV ENV_CONFIG 1
ENV RELEASE ${RELEASE}

RUN mkdir /app
COPY requirements /app/requirements
WORKDIR /app

RUN set -e \
    && pip install --no-cache -r requirements/prod.txt \
    && pip install --no-cache -r requirements/docs.txt

COPY . /app/

RUN set -e \
    && echo 'SECRET_KEY="secret"; SERVER_EMAIL="no-reply@abakus.no"' > lego/settings/local.py \
    && ENV_CONFIG=0 python manage.py collectstatic --noinput \
    && ENV_CONFIG=0 make -C docs html
