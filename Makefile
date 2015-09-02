help:
	@echo 'venv       			  - create virtualenv venv-folder'
	@echo 'lego/settings/local.py - create development local.py'
	@echo 'production             - deploy production (used by chewie)'

venv:
	virtualenv -p `which python3` venv

lego/settings/local.py:
	cp lego/settings/local_development.py lego/settings/local.py

production:
	git fetch && git reset --hard origin/master
	venv/bin/pip install -r requirements/prod.txt --upgrade
	venv/bin/python manage.py migrate
	venv/bin/python manage.py collectstatic --noinput
	touch /etc/uwsgi/apps-enabled/lego.ini

docs:
	cd docs; make html && open _build/html/index.html

.PHONY: help production docs
