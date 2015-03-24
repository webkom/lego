help:
	@echo 'dev        - install dev requirements'
	@echo 'prod       - install prod requirements'
	@echo 'venv       - create virtualenv venv-folder'
	@echo 'production - deploy production (used by chewie)'

dev:
	pip install -r requirements/dev.txt --upgrade
	pip install -r requirements/docs.txt --upgrade

prod:
	pip install -r requirements/prod.txt --upgrade

venv:
	virtualenv -p `which python3` venv

isort:
	isort -rc lego

lego/settings/local.py:
	touch lego/settings/local.py

production:
	git fetch && git reset --hard origin/master
	venv/bin/pip install -r requirements/prod.txt --upgrade
	venv/bin/python manage.py migrate
	venv/bin/python manage.py collectstatic --noinput
	touch /etc/uwsgi/apps-enabled/lego.ini

docs:
	cd docs; make html && open _build/html/index.html

.PHONY: help dev prod production docs
