from django.conf import settings
from structlog import get_logger

from lego.apps.email.models import EmailList
from lego.apps.external_sync.base import ExternalSystem
from lego.apps.external_sync.utils.gsuite import GSuiteLib

log = get_logger()


class GSuiteSystem(ExternalSystem):
    """
    Sync internal users and groups to Google GSuite.
    """

    name = 'gsuite'

    def __init__(self):
        self.gsuite = GSuiteLib()

    def migrate(self):
        pass

    def filter_users(self, queryset):
        """
        Only sync users with a password hash and internal email
        """
        return queryset\
            .exclude(crypt_password_hash='')\
            .filter(
                internal_email__isnull=False,
                internal_email_enabled=True,
                is_active=True
            )

    def filter_groups(self, queryset):
        """
        Sync groups in GSUITE_GROUPS and groups with internal_email.
        """
        return queryset.none()

    def user_exists(self, user):
        return self.gsuite.user_exists(user.internal_email_address)

    def add_user(self, user):
        return self.gsuite.add_user(
            user.id,
            user.internal_email_address,
            user.first_name,
            user.last_name,
            user.email,
            user.crypt_password_hash
        )

    def update_user(self, user):
        return self.gsuite.update_user(
            user.id,
            user.internal_email_address,
            user.first_name,
            user.last_name,
            user.email,
            user.crypt_password_hash
        )

    def delete_excess_users(self, users):
        allowed_users = [
            f'{local_part}@{settings.GSUITE_DOMAIN}'
            for local_part in users.values_list('internal_email_id', flat=True)
        ]
        existing_users = [user['primaryEmail'] for user in self.gsuite.get_all_users()]
        excess_users = set(existing_users) - set(allowed_users)
        for excess_user in excess_users:
            log.warn('delete_excess_user', system=self.name, uid=excess_user)
            self.gsuite.delete_user(excess_user)

    def group_exists(self, group):
        return False

    def add_group(self, group):
        pass

    def update_group(self, group):
        pass

    def delete_excess_groups(self, groups):
        pass

    """
    Extra sync of email lists.
    """

    def filter_extra(self):
        return [EmailList.objects.all()]

    def sync_extra(self, email_lists):
        for email_list in email_lists:
            if self.gsuite.group_exists(email_list.email_address):
                log.info('sync_update_email_list', email_list=email_list.email_address)
                self.update_email_list(email_list)
            else:
                log.info('sync_add_email_list', email_list=email_list.email_address)
                self.add_email_list(email_list)

    def add_email_list(self, email_list):
        self.gsuite.add_group(email_list.name, email_list.email_address)
        self.gsuite.set_memberships(email_list.email_address, email_list.members())

    def update_email_list(self, email_list):
        self.gsuite.update_group(email_list.email_address, email_list.name)
        self.gsuite.set_memberships(email_list.email_address, email_list.members())

    def delete_excess_extra(self, email_lists):
        """
        Please delete groups manually.
        """
        pass

    """
    Utils functions.
    """

    def set_group_members(self, group_key, members):
        desired_member_emails = set(members)

        self.gsuite.set_memberships(
            group_key=group_key,
            member_keys=desired_member_emails
        )
