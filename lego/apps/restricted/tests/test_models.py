from django.test import TestCase

from lego.apps.restricted.models import RestrictedMail


class RestrictedMailModelTestCase(TestCase):

    fixtures = ['initial_files.yaml', 'test_abakus_groups.yaml', 'test_users.yaml',
                'test_companies.yaml', 'test_events.yaml', 'test_restricted_mails.yaml']

    def test_lookup_recipients(self):
        """
        Lookup recipients, the fixtures contains duplicate users, make sure the result are correct
        """
        restricted_mail = RestrictedMail.objects.get(id=1)
        recipients = restricted_mail.lookup_recipients()

        self.assertCountEqual(recipients, [
            'test1@user.com',
            'test2@user.com'
        ])

    def test_mark_used(self):
        """The used field is not None when the item is marked as used"""
        restricted_mail = RestrictedMail.objects.get(id=1)
        restricted_mail.mark_used()
        restricted_mail.refresh_from_db()

        self.assertIsNotNone(restricted_mail.used)

    def test_lookup(self):
        """Get the restricted mail with a valid lookup"""
        restricted_mail = RestrictedMail.get_restricted_mail('test@abakus.no', 'token')
        self.assertEqual(restricted_mail.id, 1)

    def test_invalid_lookup(self):
        """Return none when an invalid lookup is performed"""
        restricted_mail = RestrictedMail.get_restricted_mail('test@abakus.no', 'invalid_token')
        self.assertIsNone(restricted_mail)
