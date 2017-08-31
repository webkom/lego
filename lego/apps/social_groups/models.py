from django.db import models

from lego.apps.social_groups.permissions import InterestGroupPermissionHandler
from lego.apps.users.models import AbakusGroup


class SocialGroup(AbakusGroup):
    # TODO: add feed
    # TODO: add picture
    description_long = models.TextField(blank=True)

    class Meta:
        abstract = True
        permission_handler = InterestGroupPermissionHandler()


class Committee(SocialGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = AbakusGroup.objects.get(name='Abakom')


class InterestGroup(SocialGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = AbakusGroup.objects.get(name='Interessegrupper')
