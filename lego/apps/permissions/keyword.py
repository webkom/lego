class KeywordPermissions:
    """
    This class manages keyword permissions.
    """

    @staticmethod
    def get_group_permissions(user):
        if user.is_anonymous():
            return set()

        perms = set()
        for group in user.all_groups:
            available_perms = group.permissions
            if available_perms:
                perms.update(available_perms)

        return perms

    @staticmethod
    def has_perm(user, perm):
        permissions = KeywordPermissions.get_group_permissions(user)
        for permission in permissions:
            if perm.startswith(permission):
                return True
        return False
