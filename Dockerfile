FROM getsentry/sentry-cli:1.63 AS sentry

ARG SENTRY_AUTH_TOKEN
ARG SENTRY_ORG
ARG SENTRY_PROJECT
ARG RELEASE

ENV SENTRY_AUTH_TOKEN=${SENTRY_AUTH_TOKEN}
ENV SENTRY_ORG=${SENTRY_ORG}
ENV SENTRY_PROJECT=${SENTRY_PROJECT}
ENV RELEASE=${RELEASE}

RUN sentry-cli releases new ${RELEASE}
RUN sentry-cli releases finalize ${RELEASE}
RUN sentry-cli releases deploys ${RELEASE} new -e "staging"
RUN sentry-cli releases deploys ${RELEASE} new -e "production"

FROM python:3.11
LABEL org.opencontainers.image.authors="webkom@abakus.no"

ARG RELEASE

ENV PYTHONPATH=/app/
ENV PYTHONUNBUFFERED=1

ENV ENV_CONFIG=1
ENV RELEASE=${RELEASE}

# Install into the image's own interpreter rather than a virtualenv, so that
# PYTHONPATH alone is enough to run the app.
ENV UV_PROJECT_ENVIRONMENT=/usr/local

# weasyprint loads pango at runtime to render the survey PDF. python:3.11
# happens to ship it, but nothing here asked for it, so a slimmer base would
# drop it and PDF export would start failing in production with a green build.
RUN set -e \
    && apt-get update \
    && apt-get install -y --no-install-recommends libpango-1.0-0 libpangoft2-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /app
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /usr/local/bin/uv

RUN set -e \
    && uv sync --frozen --no-default-groups --group docs --group prod \
    # Fail the build, rather than a request in production, if pango goes missing.
    && python -c "import weasyprint"

COPY . /app/

RUN set -e \
    && echo 'SECRET_KEY="secret"; SERVER_EMAIL="no-reply@abakus.no"' > lego/settings/local.py \
    && ENV_CONFIG=0 python manage.py collectstatic --noinput \
    && ENV_CONFIG=0 make -C docs html
