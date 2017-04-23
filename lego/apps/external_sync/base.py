from structlog import get_logger

log = get_logger()


class ExternalSystem:
    """
    External systems needs to implement a set of methods to support syncing of internal resources.
    """

    name = None

    def sync_users(self, users):
        for user in users:
            if self.user_exists(user):
                log.info('sync_update_user', user=user.username)
                self.update_user(user)
            else:
                log.info('sync_add_user', user=user.username)
                self.add_user(user)

    def sync_groups(self, groups):
        for group in groups:
            if self.group_exists(group):
                log.info('sync_update_group', group=group.name)
                self.update_group(group)
            else:
                log.info('sync_add_group', group=group.name)
                self.add_group(group)

    def migrate(self):
        """
        Prepare the system for data.
        """
        pass

    def add_user(self, user):
        """
        Add a user to the external system.
        """
        raise NotImplementedError

    def update_user(self, user):
        """
        Update a user in the external system.
        """
        raise NotImplementedError

    def delete_excess_users(self, valid_users):
        """
        Delete excess users from the remote system.
        """
        raise NotImplementedError

    def user_exists(self, user):
        """
        Check if a user already exists in the external system.
        """
        return NotImplementedError

    def add_group(self, group):
        """
        Add a group to the external system.
        """
        raise NotImplementedError

    def update_group(self, group):
        """
        Update a group in the external system.
        """
        raise NotImplementedError

    def delete_excess_groups(self, valid_groups):
        """
        Delete excess groups from the remote system.
        """
        raise NotImplementedError

    def group_exists(self, group):
        """
        Check if a group already exists in the external system.
        """
        raise NotImplementedError

    def filter_users(self, queryset):
        """
        Add a filter to the queryset if you don't want to sync all users.
        """
        return queryset

    def filter_groups(self, queryset):
        """
        Add a filter to the queryset if you don't want to sync all groups.
        """
        return queryset
