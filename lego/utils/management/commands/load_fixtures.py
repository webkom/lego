import logging
import os
from datetime import timedelta

from django.conf import settings
from django.core import serializers
from django.core.management import call_command
from django.utils import timezone

from lego.apps.events.models import Event
from lego.apps.files.models import File
from lego.apps.files.storage import storage
from lego.apps.users.fixtures.initial_abakus_groups import load_abakus_groups
from lego.apps.users.fixtures.test_abakus_groups import load_test_abakus_groups
from lego.apps.users.models import AbakusGroup, User
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Loads initial data from fixtures."

    def add_arguments(self, parser):
        parser.add_argument(
            "--development",
            action="store_true",
            default=False,
            help="Load development fixtures.",
        )
        parser.add_argument(
            "--generate", action="store_true", default=False, help="Generate fixtures"
        )

    def call_command(self, *args, **options):
        call_command(*args, verbosity=self.verbosity, **options)

    def load_fixtures(self, fixtures):
        for fixture in fixtures:
            path = "lego/apps/{}".format(fixture)
            self.call_command("loaddata", path)

    def run(self, *args, **options):
        log.info("Loading regular fixtures:")

        if options["generate"]:
            self.generate_groups()

        self.load_fixtures(
            [
                "files/fixtures/initial_files.yaml",
                "users/fixtures/initial_abakus_groups.yaml",
                "tags/fixtures/initial_tags.yaml",
                "flatpages/fixtures/initial_pages.yaml",
            ]
        )

        if getattr(settings, "DEVELOPMENT", None) or options["development"]:
            self.load_fixtures(["users/fixtures/development_users.yaml"])
            self.upload_development_files()
            log.info("Loading development fixtures:")
            self.load_fixtures(
                [
                    "users/fixtures/development_users.yaml",
                    "gallery/fixtures/development_galleries.yaml",
                    "users/fixtures/development_memberships.yaml",
                    "companies/fixtures/development_companies.yaml",
                    "events/fixtures/development_events.yaml",
                    "events/fixtures/development_pools.yaml",
                    "events/fixtures/development_registrations.yaml",
                    "articles/fixtures/development_articles.yaml",
                    "quotes/fixtures/development_quotes.yaml",
                    "podcasts/fixtures/development_podcasts.yaml",
                    'polls/fixtures/development_polls.yaml',
                    "oauth/fixtures/development_applications.yaml",
                    "reactions/fixtures/emojione_reaction_types.yaml",
                    "joblistings/fixtures/development_joblistings.yaml",
                    "surveys/fixtures/development_surveys.yaml",
                ]
            )

            self.update_event_dates()

        log.info("Done!")

    def upload_development_files(self):
        """
        Helper function for file uploads to S3
        """
        # Prepare storage bucket for development.
        # We skip this in production, where the bucket needs to be created manually.
        uploads_bucket = getattr(settings, "AWS_S3_BUCKET", None)
        log.info(f"Makes sure the {uploads_bucket} bucket exists")
        storage.create_bucket(uploads_bucket)
        assets_folder = os.path.join(settings.BASE_DIR, "../assets")
        user = User.objects.get(pk=1)
        for file in os.listdir(assets_folder):
            log.info(f"Uploading {file} file to bucket")
            file_path = os.path.join(assets_folder, file)
            storage.upload_file(uploads_bucket, file, file_path)
            File.objects.get_or_create(
                pk=file,
                defaults={
                    "state": "ready",
                    "file_type": "image",
                    "token": "token",
                    "user": user,
                    "public": True,
                },
            )

    def update_event_dates(self):
        date = timezone.now().replace(hour=16, minute=15, second=0, microsecond=0)
        for i, event in enumerate(Event.objects.all()):
            event.start_time = date + timedelta(days=i - 10)
            event.end_time = date + timedelta(days=i - 10, hours=4)
            event.save()
            for j, pool in enumerate(event.pools.all()):
                pool.activation_date = date.replace(hour=12, minute=0) + timedelta(
                    days=i - j - 16
                )
                pool.save()

    def generate_groups(self):
        self.call_command(
            "flush", "--noinput"
        )  # Need to reset the pk counter to start pk on 1
        self.call_command("migrate")
        load_test_abakus_groups()
        test_abakus_groups = AbakusGroup.objects.all()
        with open("lego/apps/users/fixtures/test_abakus_groups.yaml", "w") as f:
            f.write(
                "#\n# THIS FILE IS HANDLED BY `load_fixtures`"
                " and `development_interest_groups.py`\n#\n"
            )
            data = serializers.serialize("yaml", test_abakus_groups)
            f.write(data)

        self.call_command(
            "flush", "--noinput"
        )  # Need to reset the pk counter to start pk on 1
        self.call_command("migrate")
        self.load_fixtures(
            [
                "files/fixtures/initial_files.yaml",
                "users/fixtures/development_users.yaml",
            ]
        )
        self.upload_development_files()

        load_abakus_groups()
        abakus_groups = AbakusGroup.objects.all()
        with open("lego/apps/users/fixtures/initial_abakus_groups.yaml", "w") as f:
            f.write(
                "#\n# THIS FILE IS HANDLED BY `load_fixtures`"
                " and `initial_abakus_groups.py`\n#\n"
            )
            data = serializers.serialize("yaml", abakus_groups)
            f.write(data)
