import logging

from django.utils import timezone

from lego.apps.users.models import User
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update last login to now for ALL users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-dryrun",
            action="store_true",
            dest="no_dryrun",
            help="Do the work. No dry run",
        )

    def get_all_users(self):
        return User.objects.all()

    def update_last_login(self, user, time):
        User.objects.filter(pk=user.pk).update(last_login=time)

    def run(self, *args, **options):
        is_dryrun = not options["no_dryrun"]

        if is_dryrun:
            log.info("Running in dryrun mode")
        else:
            log.info("Running in NO-dryrun mode. Will update last login for ALL users!")

        all_users = self.get_all_users()
        new_time = timezone.now()
        log.info(
            '{:3d} users ready to update last login to "{}"'.format(
                all_users.count(), new_time
            )
        )

        if not is_dryrun:
            for user in all_users:
                self.update_last_login(user, new_time)
