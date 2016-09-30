import os

from django.conf import settings
from django.core import serializers
from django.core.management import BaseCommand

from lego.apps.articles.models import Article
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.quotes.models import Quote
from lego.apps.users.models import AbakusGroup, Membership, User


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
        self.load_from_fixture('apps/users/fixtures/initial_abakus_groups.yaml', AbakusGroup)
        self.load_from_fixture('apps/users/fixtures/initial_users.yaml', User)
        self.load_from_fixture('apps/users/fixtures/initial_memberships.yaml', Membership)

        if settings.DEVELOPMENT:
            self.stdout.write('Loading development fixtures:')
            self.load_from_fixture('apps/users/fixtures/development_users.yaml', User)
            self.load_from_fixture('apps/events/fixtures/development_events.yaml', Event)
            self.load_from_fixture('apps/events/fixtures/development_pools.yaml', Pool)
            self.load_from_fixture(
                'apps/events/fixtures/development_registrations.yaml',
                Registration
            )
            self.load_from_fixture('apps/articles/fixtures/development_articles.yaml', Article)
            self.load_from_fixture('apps/quotes/fixtures/development_quotes.yaml', Quote)
        self.stdout.write('Done!')
