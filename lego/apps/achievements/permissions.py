from lego.apps.permissions.permissions import PermissionHandler


class AchievementPermissionHandler(PermissionHandler):
    default_keyword_permission = "/sudo/admin/achievements/{perm}/"
