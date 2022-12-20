FROM getsentry/sentry-cli:1.63 as sentry

ARG SENTRY_AUTH_TOKEN
ARG SENTRY_ORG
ARG SENTRY_PROJECT
ARG RELEASE

ENV SENTRY_AUTH_TOKEN ${SENTRY_AUTH_TOKEN}
ENV SENTRY_ORG ${SENTRY_ORG}
ENV SENTRY_PROJECT ${SENTRY_PROJECT}
ENV RELEASE ${RELEASE}

RUN sentry-cli releases new ${RELEASE}
RUN sentry-cli releases finalize ${RELEASE}
RUN sentry-cli releases deploys ${RELEASE} new -e "staging"
RUN sentry-cli releases deploys ${RELEASE} new -e "production"

FROM python:3.11
LABEL org.opencontainers.image.authors="webkom@abakus.no"

ARG RELEASE

ENV PYTHONPATH /app/
ENV PYTHONUNBUFFERED 1

ENV ENV_CONFIG 1
ENV RELEASE ${RELEASE}

RUN mkdir /app
COPY requirements /app/requirements
WORKDIR /app

RUN pip install pdm

# Install prod deps, "prod" from optional section and only "docs" from dev section
RUN pdm install -G prod -G docs

COPY . /app/

RUN set -e \
    && echo 'SECRET_KEY="secret"; SERVER_EMAIL="no-reply@abakus.no"' > lego/settings/local.py \
    && ENV_CONFIG=0 python manage.py collectstatic --noinput \
    && ENV_CONFIG=0 make -C docs html
