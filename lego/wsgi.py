import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lego.settings")

from django.core.wsgi import get_wsgi_application  # isort:skip

application = get_wsgi_application()
