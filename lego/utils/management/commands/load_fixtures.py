from django.conf import settings
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Loads initial data from fixtures.'

    def handle(self, *args, **options):
        self.stdout.write('Loading regular fixtures:')

        call_command('loaddata', 'lego/apps/users/fixtures/initial_abakus_groups.yaml')
        call_command('loaddata', 'lego/apps/users/fixtures/initial_users.yaml')
        call_command('loaddata', 'lego/apps/users/fixtures/initial_memberships.yaml')

        if settings.DEVELOPMENT:
            self.stdout.write('Loading development fixtures:')
            call_command('loaddata', 'lego/apps/users/fixtures/development_users.yaml')
            call_command('loaddata', 'lego/apps/events/fixtures/development_events.yaml')
            call_command('loaddata', 'lego/apps/events/fixtures/development_pools.yaml')
            call_command('loaddata', 'lego/apps/events/fixtures/development_registrations.yaml')
            call_command('loaddata', 'lego/apps/articles/fixtures/development_articles.yaml')
            call_command('loaddata', 'lego/apps/quotes/fixtures/development_quotes.yaml')
            call_command('loaddata', 'lego/apps/oauth/fixtures/development_applications.yaml')
        self.stdout.write('Done!')
