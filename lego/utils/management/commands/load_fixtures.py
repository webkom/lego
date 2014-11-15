# -*- coding: utf8 -*-
import os

from django.contrib.auth.models import Group
from django.conf import settings
from django.core.management import BaseCommand
from django.core import serializers

from lego.app.oauth.models import APIApplication
from lego.users.models import AbakusGroup, User


def create_if_missing(obj, model):
    if not model.objects.filter(pk=obj.object.pk).exists():
        obj.save()


class Command(BaseCommand):
    help = 'Loads initial data from fixtures.'

    def load_from_fixture(self, fixture_path, model):
        self.stdout.write('Loading fixture %s' % fixture_path)

        fixture_file = os.path.join(settings.BASE_DIR, fixture_path)

        with open(fixture_file) as fixture:
            for obj in serializers.deserialize('yaml', fixture):
                create_if_missing(obj, model)

    def handle(self, *args, **options):
        self.stdout.write('Loading regular fixtures:')
        self.load_from_fixture('users/fixtures/initial_permission_groups.yaml', Group)
        self.load_from_fixture('users/fixtures/initial_abakus_groups.yaml', AbakusGroup)
        self.load_from_fixture('users/fixtures/initial_users.yaml', User)
        self.load_from_fixture('app/oauth/fixtures/initial_applications.yaml', APIApplication)

        if settings.DEVELOPMENT:
            self.stdout.write('Loading development fixtures:')
            self.load_from_fixture('users/fixtures/development_users.yaml', User)
            self.load_from_fixture('app/oauth/fixtures/development_applications.yaml',
                                   APIApplication)

        self.stdout.write('Done!')
