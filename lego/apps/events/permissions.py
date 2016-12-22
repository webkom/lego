import requests
from django.conf import settings
from structlog import get_logger

from lego.apps.permissions.permissions import AbakusPermission

log = get_logger()


class NestedEventPermissions(AbakusPermission):
    def has_object_permission(self, request, view, obj):
        obj = obj.event
        return super().has_object_permission(request, view, obj)


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
