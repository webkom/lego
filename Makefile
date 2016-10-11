help:
	@echo 'lego/settings/local.py - create empty lego/settings/local.py for testing'
	@echo 'docs                   - build and display docss
	@echo 'ci_settings            - create a lego/settings/local.py for ci'

lego/settings/local.py:
	touch lego/settings/local.py

docs:
	cd docs; make html && open _build/html/index.html

ci_settings:
	echo "from .test import *" > lego/settings/local.py

.PHONY: help docs ci_settings
