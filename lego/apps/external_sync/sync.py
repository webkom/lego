from structlog import get_logger

from lego.apps.users.models import AbakusGroup, User

from .external.ldap import LDAPSystem

log = get_logger()


class Sync:
    """
    Export users and groups to external systems.
    We should split this into multiple celery tasks and add a lock at a later point.
    """

    def __init__(self):
        self.systems = [
            LDAPSystem(),
            # GSuiteSystem(),
        ]

    def lookup_querysets(self):
        users = User.objects.all()
        groups = AbakusGroup.objects.all()
        return users, groups

    def sync(self):

        users, groups = self.lookup_querysets()

        for system in self.systems:
            log.info('sync_migrate', system=system.name)
            system.migrate()

            sync_users = system.filter_users(users)
            sync_groups = system.filter_groups(groups)

            log.info('sync_users', system=system.name, users=sync_users.count())
            system.sync_users(sync_users)

            log.info('sync_groups', system=system.name, groups=sync_groups.count())
            system.sync_groups(sync_groups)

            log.info('delete_excess_groups', system=system.name)
            system.delete_excess_groups(sync_groups)

            log.info('delete_excess_users', system=system.name)
            system.delete_excess_users(sync_users)

            log.info('sync_done', system=system.name)
