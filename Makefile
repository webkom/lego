help:
	@echo 'lego/settings/local.py - create empty lego/settings/local.py for testing'
	@echo 'docs                   - build and display docs'
	@echo 'ci_settings            - create a lego/settings/local.py for ci'
	@echo 'fixme                  - fix code formatting'
	@echo 'devenv                 - creates a disposable devenv'

lego/settings/local.py:
	touch lego/settings/local.py

docs:
	cd docs; make html && open _build/html/index.html

ci_settings:
	echo "from .test import *" > lego/settings/local.py

fixme:
	uv run --only-group lint ruff check --fix lego
	uv run --only-group lint ruff format lego

# UV_PROJECT_ENVIRONMENT keeps the container venv out of the bind mount, so it
# cannot overwrite the host .venv with a linux one.
devenv:
	docker run --net=host --rm -v "${PWD}:/code" -e UV_PROJECT_ENVIRONMENT=/tmp/venv -it abakus/lego-testbase:python3.11 "bash" "-c" "cd /code && pip install -q uv==0.11.6 && uv sync --frozen --all-groups && exec bash"

.PHONY: help docs ci_settings fixme devenv
