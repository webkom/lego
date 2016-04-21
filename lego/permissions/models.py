from django.db import models
from django.utils.translation import ugettext_lazy as _

from lego.permissions.managers import PublicObjectPermissionsManager
from lego.users.models import AbakusGroup, User


def _check_intersection(first, second):
    return len(set(first).intersection(set(second))) > 0


class ObjectPermissionsModel(models.Model):
    """
    Abstract model that provides fields that can be used for object permissions.
    """

    can_edit_users = models.ManyToManyField(User, related_name='can_edit_%(class)s', blank=True)

    can_edit_groups = models.ManyToManyField(AbakusGroup, related_name='can_edit_%(class)s',
                                             blank=True)

    can_view_groups = models.ManyToManyField(AbakusGroup, related_name='can_view_%(class)s',
                                             blank=True)

    require_auth = models.BooleanField(_('require auth'), default=False)

    public_objects = PublicObjectPermissionsManager()

    class Meta:
        abstract = True

    def needs_auth(self):
        return self.require_auth or self.can_view_groups.count() > 0

    def can_view(self, user):
        """
        Checks if a user can view this object

        :param user:
        :rtype: bool
        """

        if not user.is_authenticated():
            return not self.needs_auth() and self.can_view_groups.count() == 0

        can_view_groups = self.can_view_groups.all()

        if not can_view_groups:
            return True
        return (user == getattr(self, 'created_by', False) or
                _check_intersection(user.all_groups, can_view_groups))

    def can_edit(self, user):
        """
        Checks if a user can edit this object

        :rtype: bool
        """

        if not user.is_authenticated():
            return not self.needs_auth() and self.can_view_groups.count() == 0

        return (user == getattr(self, 'created_by', False) or user in self.can_edit_users.all() or
                _check_intersection(user.all_groups, self.can_edit_groups.all()))
