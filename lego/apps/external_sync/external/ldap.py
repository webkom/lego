from django.conf import settings
from structlog import get_logger

from lego.apps.external_sync.base import ExternalSystem
from lego.apps.external_sync.utils.ldap import LDAPLib

log = get_logger()


class LDAPSystem(ExternalSystem):
    """
    Sync internal users and groups to a LDAP directory.

    user DN: uid={username},ou=users,dc=abakus,dc=no
    group DN: cn={group_name},ou=groups,dc=abakus,dc=no

    Usernames should not change, this will cause the sync to create a new user.
    We need to make sure the group name is unique because this is a part of the
    group DN. We may consider use the full group path as the group name (Users/Abakus/Webkom)

    TODO: Have a look at group names.
    """

    name = 'ldap'

    def __init__(self):
        self.ldap = LDAPLib()

    def migrate(self):
        """
        Make sure the ou's exists in LDAP before we create user and group entries.
        """
        self.ldap.update_organization_unit('users')
        self.ldap.update_organization_unit('groups')

    def filter_users(self, queryset):
        """
        Only sync users with a password hash.
        """
        return queryset.exclude(ldap_password_hash='')

    def filter_groups(self, queryset):
        """
        Sync groups in LDAP_GROUPS
        """
        return queryset.filter(name__in=settings.LDAP_GROUPS)

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
        """
        We only modify the password if it is different from the one stored in our database.
        """
        if not self.ldap.check_password(user.username, user.ldap_password_hash):
            log.info('external_password_update', system=self.name, uid=user.username)
            self.ldap.change_password(user.username, user.ldap_password_hash)

    def delete_excess_users(self, users):
        allowed_users = users.values_list('username', flat=True)
        existing_users = map(lambda user: str(user.uid), self.ldap.get_all_users())
        excess_users = set(existing_users) - set(allowed_users)
        for excess_user in excess_users:
            log.warn('delete_excess_user', system=self.name, uid=excess_user)
            self.ldap.delete_user(excess_user)

    def group_exists(self, group):
        return bool(self.ldap.search_group(group.id))

    def add_group(self, group):
        members = group.memberships.values_list('user__username')
        self.ldap.add_group(
            group.id, group.name
        )
        print(members)

    def update_group(self, group):
        members = group.memberships.values_list('user__username')
        print(members)

    def delete_excess_groups(self, groups):
        allowed_groups = groups.values_list('name', flat=True)
        existing_groups = map(lambda group: str(group.cn), self.ldap.get_all_groups())
        excess_groups = set(existing_groups) - set(allowed_groups)
        for excess_group in excess_groups:
            log.warn('delete_excess_group', cn=excess_group)
            self.ldap.delete_group(excess_group)
