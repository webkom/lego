# -*- coding: utf8 -*-

import os

from django.core import serializers
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from lego import settings
from lego.users.models import AbakusGroup


def create_if_missing(group):
    try:
        AbakusGroup.objects.get(id=group.object.id)
    except AbakusGroup.DoesNotExist:
        group.save()


def load_groups():
    group_path = os.path.join(settings.BASE_DIR, 'users', 'fixtures', 'initial_groups.yaml')

    with open(group_path) as init_groups:
        for group in serializers.deserialize('yaml', init_groups):
            create_if_missing(group)

@receiver(post_migrate)
def load_initial_data(sender, **kwargs):
    load_groups()
