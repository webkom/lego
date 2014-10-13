# -*- coding: utf8 -*-

import os

from django.core import serializers
from django.db.models.signals import post_migrate

from lego import settings
from lego.users.models import AbakusGroup


def create_if_missing(obj, model):
    if not model.objects.filter(pk=obj.object.pk).exists():
        obj.save()


def load_from_fixture(fixture_path, model):
    fixture_file = os.path.join(settings.BASE_DIR, fixture_path)

    with open(fixture_file) as fixture:
        for obj in serializers.deserialize('yaml', fixture):
            create_if_missing(obj, model)


def load_fixture_callback(sender, **kwargs):
        load_from_fixture('users/fixtures/initial_groups.yaml', AbakusGroup)


def attach_signals():
    post_migrate.connect(load_fixture_callback)
