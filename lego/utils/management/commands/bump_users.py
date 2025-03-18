import logging
from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from lego.apps.users.constants import DATA_LONG, GROUP_INTEREST, KOMTEK_LONG
from lego.apps.users.models import AbakusGroup, Membership, User
from lego.utils.management_command import BaseCommand

log = logging.getLogger(__name__)

other_student_groups_names = ["Students", DATA_LONG, KOMTEK_LONG]

data_groups_names = [
    f"1. klasse {DATA_LONG}",
    f"2. klasse {DATA_LONG}",
    f"3. klasse {DATA_LONG}",
    f"4. klasse {DATA_LONG}",
    f"5. klasse {DATA_LONG}",
]

komtek_groups_names = [
    f"1. klasse {KOMTEK_LONG}",
    f"2. klasse {KOMTEK_LONG}",
    f"3. klasse {KOMTEK_LONG}",
    f"4. klasse {KOMTEK_LONG}",
    f"5. klasse {KOMTEK_LONG}",
]

timedelta_since_prev_bump = timedelta(days=5 * 31)


class Command(BaseCommand):
    help = "Bumps users to the next grade"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-dryrun",
            action="store_true",
            dest="no_dryrun",
            help="Do the work. No dry run",
        )

    def get_group(self, name):
        group = AbakusGroup.objects.filter(name=name).first()
        if not group:
            raise ValueError(f'Could not find group with name "{name}"')
        return group

    def get_students_in_group(self, group):
        return self.get_students_in_groups([group])

    def get_students_in_groups(self, groups):
        return (
            User.all_objects.filter(abakus_groups__in=groups)
            .filter(
                Q(date_bumped__lte=timezone.now() - timedelta_since_prev_bump)
                | Q(date_bumped=None)
            )
            .prefetch_related("abakus_groups")
        )

    def verify_no_duplicate_memberships(self, student_groups):
        students = self.get_students_in_groups(student_groups)
        log.info(f"Student count: {students.count()}")
        users_with_multiple_memberships = (
            students.annotate(Count("id")).order_by().filter(id__count__gt=1)
        )

        if users_with_multiple_memberships.count() == 0:
            return

        for user in users_with_multiple_memberships:
            log.error(
                'User "{}" has multiple student memberships: {}'.format(
                    user,
                    user.abakus_groups.filter(
                        pk__in=[group.pk for group in student_groups]
                    ),
                )
            )
        raise ValueError("Found duplicate student memberships")

    def get_groups(self, names):
        return [self.get_group(name) for name in names]

    def change_user_grade(self, user, from_grade, to_grade):
        with transaction.atomic():
            from_grade.remove_user(user)
            if to_grade:
                to_grade.add_user(user)
            else:
                for membership in Membership.objects.filter(
                    user=user, abakus_group__type=GROUP_INTEREST
                ):
                    membership.delete(force=True)
            User.objects.filter(pk=user.pk).update(date_bumped=timezone.now())

    def run(self, *args, **options):
        is_dryrun = not options["no_dryrun"]

        if is_dryrun:
            log.info("Running in dryrun mode")
        else:
            log.info("Running in NO-dryrun mode. Will execute bump")
        data_groups = self.get_groups(data_groups_names)
        komtek_groups = self.get_groups(komtek_groups_names)
        other_student_groups = self.get_groups(other_student_groups_names)

        self.verify_no_duplicate_memberships(
            data_groups + komtek_groups + other_student_groups
        )

        for groups in [data_groups, komtek_groups]:
            for grade_index in range(len(groups)):
                from_group = groups[grade_index]
                to_group = (
                    None if grade_index + 1 is len(groups) else groups[grade_index + 1]
                )
                to_group_name = to_group.name if to_group else None
                students_in_group = self.get_students_in_group(from_group)
                log.info(
                    '{:3d} users ready to be bumped from "{}" to "{}"'.format(
                        students_in_group.count(), from_group.name, to_group_name
                    )
                )
                if is_dryrun:
                    continue
                for user in students_in_group:
                    self.change_user_grade(user, from_group, to_group)
