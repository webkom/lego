import requests
from django.conf import settings
from structlog import get_logger

from lego.apps.users.models import AbakusGroup

log = get_logger()


def verify_captcha(captcha_response):
    try:
        r = requests.post(settings.CAPTCHA_URL, {
            'secret': settings.CAPTCHA_KEY,
            'response': captcha_response
        })
        return r.json().get('success', False)
    except requests.exceptions.RequestException as e:
        log.error('captcha_validation_error', exception=e,
                  captcha_url=settings.CAPTCHA_URL, captcha_response=captcha_response)
        return False


def insert_abakus_groups(tree, parent=None):
    for key, value in tree.items():
        kwargs = value[0]
        if 'id' in kwargs:
            node = AbakusGroup.objects.update_or_create(
                id=kwargs['id'], name=key, defaults={**kwargs, 'parent': parent}
            )[0]
        else:
            node = AbakusGroup.objects.update_or_create(
                name=key, defaults={**kwargs, 'parent': parent}
            )[0]
        insert_abakus_groups(value[1], node)
