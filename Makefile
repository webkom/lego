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
	docker run --rm -v "${PWD}:/code" -it python:3.11 "bash" "-c" "cd /code && pip install -r requirements/black.txt -r requirements/isort.txt && isort lego && black lego"

devenv:
	docker run --net=host --rm -v "${PWD}:/code" -it python:3.11 "bash" "-c" "cd /code && pip install -r requirements/dev.txt && exec bash"

.PHONY: help docs ci_settings fixme devenv
