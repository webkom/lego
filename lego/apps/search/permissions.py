from lego.apps.permissions.constants import VIEW


def has_permission(instance, user):
    return user.has_perm(VIEW, instance)
