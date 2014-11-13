help:
	@echo 'dev        - install dev requirements'
	@echo 'prod       - install prod requirements'
	@echo 'venv       - create virtualenv venv-folder'
	@echo 'production - deploy production (used by chewie)'

dev:
	pip install -r requirements/dev.txt --upgrade

prod:
	pip install -r requirements/prod.txt --upgrade

venv:
	virtualenv -p `which python3` venv

lego/settings/local.py:
	touch lego/settings/local.py

production:
	git fetch && git reset --hard origin/master
	venv/bin/pip install -r requirements/prod.txt --upgrade
	venv/bin/python manage.py migrate
	venv/bin/python manage.py collectstatic --noinput
	touch /etc/uwsgi/apps-enabled/lego.ini

.PHONY: help dev prod production
