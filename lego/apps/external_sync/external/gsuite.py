from lego.apps.email.models import EmailList
from lego.apps.external_sync.base import ExternalSystem
from lego.apps.external_sync.utils.gsuite import GSuiteLib
from lego.apps.users.models import AbakusGroup


class GSuiteSystem(ExternalSystem):

    name = 'gsuite'

    def __init__(self):
        self.gsuite = GSuiteLib()

    def filter_users(self, queryset):
        """
        These values are required by GSuite in order to create a user account
        """
        return queryset\
            .filter(internal_email__isnull=False)\
            .filter(first_name__isnull=False)\
            .filter(last_name__isnull=False)

    def filter_groups(self, queryset):
        # TODO: Fix Sync class
        return EmailList.objects.all()

    def add_user(self, user):
        gsuite_user_object = dict(
            name=dict(
                givenName=user.first_name,
                familyName=user.last_name
            ),
            password='test1234', # TODO: generate randomly and send an email to @stud email with the password
            changePasswordAtNextLogin=True,
            primaryEmail=user.internal_email.email
        )
        self.gsuite.create_user(gsuite_user_object)

    def update_user(self, user):
        pass

    def delete_excess_users(self, valid_users):
        """
        We should not automatically delete gsuite users since they can have lots of emails and
        drive documents. We should review all deletions manually and delete them in bulk.
        This function can flag groups and send a notification to administrators.
        """
        pass

    def user_exists(self, user):
        return self.gsuite.user_exists(user.internal_email.email)

    def add_group(self, email_list):
        gsuite_group_object = dict(
            email=email_list.email_address.email
        )
        self.gsuite.create_group(gsuite_group_object)
        self.update_group(email_list)

    def update_group(self, email_list):
        members = set(email_list.users.all())
        for group in email_list.groups.all():
            members = members.union(set([membership.user for membership in group.memberships.all()]))

        desired_member_emails = [
            user.internal_email.email if user.internal_email else user.email
            for user in members
            if user.internal_email or user.email
        ]

        self.gsuite.set_memberships(
            group_key=email_list.email_address.email,
            member_keys=desired_member_emails
        )


    def delete_excess_groups(self, valid_groups):
        """
        We should not automatically delete gsuite groups since they can have lots of emails and
        drive documents. We should review all deletions manually and delete them in bulk.
        This function can flag groups and send a notification to administrators.
        """
        pass

    def group_exists(self, email_list):
        return self.gsuite.group_exists(email_list.email_address.email)







if __name__ == '__main__':
    system = GSuiteSystem()
    group = AbakusGroup.objects.get(name='Abakom')

    system.add_group(group)
