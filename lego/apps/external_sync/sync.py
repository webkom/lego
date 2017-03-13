from structlog import get_logger

from lego.apps.users.models import AbakusGroup, User

from .external.ldap import LDAPSystem

log = get_logger()


class Sync:
    """
    Export users and groups to external systems.
    We split this into multiple celery tasks at a later point.
    """

    def __init__(self):
        self.systems = [
            LDAPSystem(),
            # GSuiteSystem(),
        ]

    def sync(self):
        users = User.objects.all()
        groups = AbakusGroup.objects.all()

        for system in self.systems:
            log.info('sync_migrate', system=system.name)
            system.migrate()

            log.info('sync_users', system=system.name, users=users.count())
            system.sync_users(filter(system.should_sync_user, users))

            log.info('sync_groups', system=system.name, groups=groups.count())
            system.sync_groups(filter(system.should_sync_group, groups))

            log.info('sync_done', system=system.name)
