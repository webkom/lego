from datetime import timedelta

from django.core.management import call_command
from django.db import transaction
from django.utils import timezone

from lego.apps.users.constants import GROUP_INTEREST
from lego.apps.users.models import AbakusGroup, Membership, User
from lego.utils.test_utils import BaseTestCase


def get_groups(user):
    return list(user.abakus_groups.all())


def bump_users(dry_run=False):
    call_command("bump_users", "--no-dryrun")


def reset_user_bump_date(user, months=10):
    date_bumped = timezone.now() - timedelta(days=months * 31)
    user.date_bumped = date_bumped
    user.save()


class AbakusGroupHierarchyTestCase(BaseTestCase):
    fixtures = ["initial_files.yaml", "initial_abakus_groups.yaml"]

    def setUp(self):
        self.students = AbakusGroup.objects.get(name="Students")

        self.data = AbakusGroup.objects.get(name="Datateknologi")
        self.data_1 = AbakusGroup.objects.get(name="1. klasse Datateknologi")
        self.data_2 = AbakusGroup.objects.get(name="2. klasse Datateknologi")
        self.data_3 = AbakusGroup.objects.get(name="3. klasse Datateknologi")
        self.data_4 = AbakusGroup.objects.get(name="4. klasse Datateknologi")
        self.data_5 = AbakusGroup.objects.get(name="5. klasse Datateknologi")

        self.komtek = AbakusGroup.objects.get(name="Kommunikasjonsteknologi")
        self.komtek_1 = AbakusGroup.objects.get(
            name="1. klasse Kommunikasjonsteknologi"
        )
        self.komtek_2 = AbakusGroup.objects.get(
            name="2. klasse Kommunikasjonsteknologi"
        )
        self.komtek_3 = AbakusGroup.objects.get(
            name="3. klasse Kommunikasjonsteknologi"
        )
        self.komtek_4 = AbakusGroup.objects.get(
            name="4. klasse Kommunikasjonsteknologi"
        )
        self.komtek_5 = AbakusGroup.objects.get(
            name="5. klasse Kommunikasjonsteknologi"
        )

        self.user = User.objects.create()
        reset_user_bump_date(self.user)

    def test_bump_data(self):
        """Data students should be bumped"""
        user = self.user
        self.data_1.add_user(user)
        self.assertEqual(get_groups(user), [self.data_1])

        bump_users()
        reset_user_bump_date(user)
        self.assertEqual(get_groups(user), [self.data_2])

        bump_users()
        reset_user_bump_date(user)
        self.assertEqual(get_groups(user), [self.data_3])

        bump_users()
        reset_user_bump_date(user)
        self.assertEqual(get_groups(user), [self.data_4])

        bump_users()
        reset_user_bump_date(user)
        self.assertEqual(get_groups(user), [self.data_5])

        bump_users()
        reset_user_bump_date(user)
        self.assertEqual(get_groups(user), [])

    def test_bump_komtek(self):
        """Komtek students should be bumped"""
        user = self.user
        self.komtek_1.add_user(user)
        self.assertEqual(get_groups(user), [self.komtek_1])

        bump_users()
        reset_user_bump_date(user)
        self.assertEqual(get_groups(user), [self.komtek_2])

        bump_users()
        reset_user_bump_date(user)
        self.assertEqual(get_groups(user), [self.komtek_3])

        bump_users()
        reset_user_bump_date(user)
        self.assertEqual(get_groups(user), [self.komtek_4])

        bump_users()
        reset_user_bump_date(user)
        self.assertEqual(get_groups(user), [self.komtek_5])

        bump_users()
        reset_user_bump_date(user)
        self.assertEqual(get_groups(user), [])

    def test_bump_komtek_interest_remove(self):
        """5th grade interestgroup should not be member afterwards"""
        user = self.user
        self.komtek_5.add_user(user)
        self.assertEqual(get_groups(user), [self.komtek_5])
        abacraft = AbakusGroup.objects.create(name="AbaCraft", type=GROUP_INTEREST)
        abacraft.add_user(user)
        bump_users()
        reset_user_bump_date(user)
        transaction.on_commit(lambda: self.assertEqual(get_groups(user), []))
        transaction.on_commit(
            lambda: self.assertFalse(
                Membership.objects.filter(
                    user=user, abakus_group__type=GROUP_INTEREST
                ).exists()
            )
        )

    def test_multibump_should_not_bump(self):
        """Bumping multiple times should not bump the same user more than once"""
        user = self.user
        self.komtek_1.add_user(user)
        self.assertEqual(get_groups(user), [self.komtek_1])
        bump_users()
        bump_users()
        bump_users()
        self.assertEqual(get_groups(user), [self.komtek_2])

    def test_bump_after_recent_bump(self):
        """Bumping short after last bump should not bump the same user more than once"""
        user = self.user
        self.komtek_1.add_user(user)
        reset_user_bump_date(user, months=2)
        bump_users()
        bump_users()
        self.assertEqual(get_groups(user), [self.komtek_1])

    def test_discover_users_with_two_grades(self):
        """It should exit if a user has two grades"""
        user = self.user
        self.komtek_1.add_user(user)
        self.data_1.add_user(user)
        with self.assertRaises(SystemExit):
            bump_users()

    def test_discover_users_in_data_or_komtek_group(self):
        """It should exit if a user is member of a grade and the Data/komtek group"""
        user = self.user
        grade = self.komtek_4
        main_group = self.komtek
        grade.add_user(user)
        bump_users()
        reset_user_bump_date(user)

        main_group.add_user(user)
        with self.assertRaises(SystemExit):
            bump_users()

    def test_discover_users_in_students_group(self):
        """It should exit if a user is member of a grade and the Students group"""
        user = self.user
        self.komtek_1.add_user(user)
        self.students.add_user(user)
        with self.assertRaises(SystemExit):
            bump_users()
