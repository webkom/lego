from django.conf import settings

from lego.apps.external_sync.base import ExternalSystem
from lego.apps.external_sync.utils.ldap import LDAPLib


class LDAPSystem(ExternalSystem):

    name = 'ldap'

    def __init__(self):
        self.ldap = LDAPLib()

    def migrate(self):
        """
        Make sure the ou's exists in LDAP before we create user and group entries.
        """
        self.ldap.update_organization_unit('users')
        self.ldap.update_organization_unit('groups')

    def should_sync_user(self, user):
        """
        Only sync users with a password hash.
        """
        return bool(user.ldap_password_hash)

    def should_sync_group(self, group):
        """
        Sync committees and groups in LDAP_GROUPS
        """
        return group.is_committee or group.name in settings.LDAP_GROUPS

    def user_exists(self, user):
        return bool(self.ldap.search_user(user.username))

    def add_user(self, user):
        self.ldap.add_user(
            user.username,
            user.first_name,
            user.last_name,
            user.email,
            user.ldap_password_hash
        )

    def update_user(self, user):
        pass

    def group_exists(self, group):
        return bool(self.ldap.search_group(group.id))

    def add_group(self, group):
        self.ldap.add_group(group.id, group.name.lower())

    def update_group(self, group):
        pass
