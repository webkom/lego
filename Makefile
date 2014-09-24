
dev:
	pip install -r requirements/dev.txt --upgrade
	
prod:
	pip install -r requirements/prod.txt --upgrade

venv:
	virtualenv -p `which python3` venv

lego/settings/local.py:
	touch lego/settings/local.py
