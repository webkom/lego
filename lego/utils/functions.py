from datetime import datetime
from typing import Optional
from urllib.parse import quote

from django.conf import settings
from rest_framework.response import Response

import requests
from structlog import get_logger

from lego.apps.users.models import AbakusGroup
from lego.utils.models import BasisModel

log = get_logger()


def verify_captcha(captcha_response):
    try:
        r = requests.post(
            settings.CAPTCHA_URL,
            {"secret": settings.CAPTCHA_KEY, "response": captcha_response},
        )
        return r.json().get("success", False)
    except requests.exceptions.RequestException as e:
        log.error(
            "captcha_validation_error",
            exception=e,
            captcha_url=settings.CAPTCHA_URL,
            captcha_response=captcha_response,
        )
        return False


def insert_abakus_groups(tree, parent=None):
    for key, value in tree.items():
        kwargs = value[0]
        if "id" in kwargs:
            node = AbakusGroup.objects.update_or_create(
                id=kwargs["id"], name=key, defaults={**kwargs, "parent": parent}
            )[0]
        else:
            node = AbakusGroup.objects.update_or_create(
                name=key, defaults={**kwargs, "parent": parent}
            )[0]
        insert_abakus_groups(value[1], node)


def request_plausible_statistics(obj: BasisModel, url_root: Optional[str]) -> Response:
    created_at = obj.created_at.strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%d")
    date = f"{created_at},{now}"  # Plausible wants the date on this schema: YYYY-MM-DD,YYYY-MM-DD
    url_path = f"/{url_root or (obj._meta.model_name + 's')}/{obj.id}"
    filters = f"event:page=={quote(url_path)}"

    api_url = (
        "https://ls.webkom.dev/api/v1/stats/timeseries"
        "?site_id=abakus.no"
        "&metrics=visitors,pageviews,bounce_rate,visit_duration"
        "&period=custom&date={date}"
        "&filters={filters}"
    ).format(date=date, filters=filters)

    headers = {
        "Authorization": f"Bearer {settings.PLAUSIBLE_KEY}",
        "Content-Type": "application/json",
    }

    return requests.get(api_url, headers=headers)
