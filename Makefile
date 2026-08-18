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
	docker run --rm -v "${PWD}:/code" -it abakus/lego-testbase:python3.11 "bash" "-c" "cd /code && pip install -q uv==0.11.6 && uv run --frozen --only-group lint ruff check --fix lego && uv run --frozen --only-group lint ruff format lego"

devenv:
	docker run --net=host --rm -v "${PWD}:/code" -it abakus/lego-testbase:python3.11 "bash" "-c" "cd /code && pip install -q uv==0.11.6 && uv sync --frozen --all-groups && exec bash"

.PHONY: help docs ci_settings fixme devenv
