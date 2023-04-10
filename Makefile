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
	docker run --rm -v "${PWD}:/code" -it abakus/lego-testbase:python3.11 "bash" "-c" "cd /code && tmpdir=$(mktemp -d) && python -m venv $$tmpdir/venv && . $$tmpdir/venv/bin/activate && poetry install --only formatting && isort lego && black lego && rm -rf $$tmpdir"

devenv:
	docker run --net=host --rm -v "${PWD}:/code" -it abakus/lego-testbase:python3.11 "bash" "-c" "cd /code && poetry install && exec bash"

.PHONY: help docs ci_settings fixme devenv
