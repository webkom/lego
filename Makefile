help:
	@echo 'lego/settings/local.py - create empty lego/settings/local.py for testing'
	@echo 'docs                   - build and display docs'
	@echo 'ci_settings            - create a lego/settings/local.py for ci'
	@echo 'fixme                  - Fix code formatting'

lego/settings/local.py:
	touch lego/settings/local.py

docs:
	cd docs; make html && open _build/html/index.html

ci_settings:
	echo "from .test import *" > lego/settings/local.py

fixme:
	docker run --rm -v ${PWD}:/code -it python:3.7-slim "bash" "-c" "cd /code && pip install -r requirements/black.txt -r requirements/isort.txt && isort -rc lego && black lego"

.PHONY: help docs ci_settings
