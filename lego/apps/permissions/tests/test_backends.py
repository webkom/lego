from django.test import TestCase

from lego.apps.events.models import Event
from lego.apps.users.models import AbakusGroup, User


class AbakusBackendTestCase(TestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_events.yaml',
                'test_companies.yaml', 'test_users.yaml']

    def setUp(self):
        self.test_user = User.objects.get(username='useradmin_test')
        self.useradmin_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_group.add_user(self.test_user)
        self.event = Event.objects.all().first()

    def test_has_perm_exact(self):
        has_perm = self.test_user.has_perm('users.user.list')
        self.assertTrue(has_perm)

    def test_has_perm_starts_with_correct(self):
        """Test that user with prefix /sudo/admin/ has permission to /sudo/admin/events/... etc"""
        new_group = AbakusGroup.objects.create(name='new', permissions=['/sudo/admin/'])
        new_group.add_user(self.test_user)
        self.assertTrue(self.test_user.has_perm('events.event.update'))

    def test_with_view_object_permissions_passing(self):
        """Test that user with can_view has permission to retrieve using permission string"""
        self.event.can_view_groups.add(self.useradmin_group)
        self.assertTrue(self.test_user.has_perm('events.event.retrieve', self.event))

    def test_with_view_object_permissions_failing(self):
        """Test that user with can_view has permission to retrieve using permission string"""
        self.assertFalse(self.test_user.has_perm('events.event.retrieve', self.event))

    def test_with_view_object_permissions_when_editing(self):
        """Test that user with can_view fails when trying to edit using permission string"""
        self.event.can_view_groups.add(self.useradmin_group)
        self.assertFalse(self.test_user.has_perm('events.event.update', self.event))

    def test_with_edit_object_permissions(self):
        """Test that user with can_edit has permission to edit using permission string"""
        self.event.can_edit_users.add(self.test_user)
        self.assertTrue(self.test_user.has_perm('events.event.update', self.event))

    def test_with_keyword_permission(self):
        """Test that user with keyword permission has permission to edit using permission string"""
        new_group = AbakusGroup.objects.create(
            name='new', permissions=['/sudo/admin/events/update']
        )
        new_group.add_user(self.test_user)
        self.assertTrue(self.test_user.has_perm('events.event.update'))

    def test_without_permissions(self):
        """Test that user does not have permission when not having permissions"""
        event = Event.objects.all().first()
        self.assertFalse(self.test_user.has_perm('events.event.update', event))

    def test_has_perm_incorrect(self):
        """Test that non existant permission string check fails"""
        has_perm = self.test_user.has_perm('users.user.feil')
        self.assertFalse(has_perm)
