help:
	@echo 'venv       			  - create virtualenv venv-folder'
	@echo 'lego/settings/local.py - create development local.py'
	@echo 'production             - deploy production (used by chewie)'
	@echo 'development            - install dev requirements, setup local.py and run migrations

venv:
	virtualenv -p `which python3` venv

local:
	echo "from .development import *" > lego/settings/local.py

development: local
	venv/bin/pip install -r requirements/dev.txt --upgrade
	venv/bin/pip install -r requirements/docs.txt --upgrade
	venv/bin/python manage.py migrate

production:
	git fetch && git reset --hard origin/master
	venv/bin/pip install -r requirements/prod.txt --upgrade
	venv/bin/python manage.py migrate

docs:
	cd docs; make html && open _build/html/index.html

test:
	echo "from .test import *" > lego/settings/local.py


.PHONY: help development production docs test
