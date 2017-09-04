from django.db import models

models.options.DEFAULT_NAMES += ('permission_handler', )


class ObjectPermissionsModel(models.Model):
    """
    Abstract model that provides fields that can be used for object permissions.
    """

    can_edit_users = models.ManyToManyField(
        'users.User', related_name='can_edit_%(class)s', blank=True
    )
    can_edit_groups = models.ManyToManyField(
        'users.AbakusGroup', related_name='can_edit_%(class)s', blank=True
    )
    can_view_groups = models.ManyToManyField(
        'users.AbakusGroup', related_name='can_view_%(class)s', blank=True
    )

    require_auth = models.BooleanField(default=True)

    class Meta:
        abstract = True
