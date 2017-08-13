from django.core.exceptions import ImproperlyConfigured
from structlog import get_logger

from lego.apps.external_sync.external.gsuite import GSuiteSystem
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
        ]

        try:
            gsuite = GSuiteSystem()
            self.systems.append(gsuite)
        except ImproperlyConfigured:
            pass

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

            extra_filter = getattr(system, 'filter_extra', None)
            if extra_filter:
                """
                Sync extras if the system has implemented the 'filter_extra' function.
                """
                extras = extra_filter()

                log.info('sync_extra', system=system.name)
                system.sync_extra(*extras)

                log.info('delete_excess_extra', system=system.name)
                system.delete_excess_extra(*extras)

            log.info('sync_done', system=system.name)
