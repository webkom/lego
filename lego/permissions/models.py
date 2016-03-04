from basis.models import BasisModel
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

    can_edit_users = models.ManyToManyField(User, related_name='can_edit_%(class)s', blank=True,
                                            null=True)

    can_edit_groups = models.ManyToManyField(AbakusGroup,
                                             related_name='can_edit_%(class)s', blank=True,
                                             null=True)

    can_view_groups = models.ManyToManyField(AbakusGroup,
                                             related_name='can_view_%(class)s', blank=True,
                                             null=True)

    require_auth = models.BooleanField(_('require auth'), default=False)

    public_objects = PublicObjectPermissionsManager()

    class Meta:
        abstract = True

    def needs_auth(self):
        return self.require_auth or len(self.can_view_groups.all()) > 0

    def can_view(self, user):
        """
        Checks if a user can view this object

        :param user:
        :rtype: bool
        """

        if not user.is_authenticated():
            return not self.needs_auth()

        return (user == self.created_by or
                _check_intersection(user.all_groups, self.can_view_groups.all()))

    def can_edit(self, user):
        """
        Checks if a user can edit this object

        :rtype: bool
        """

        if not user.is_authenticated():
            return not self.needs_auth()

        return (user == self.created_by or
                user in self.can_edit_users.all() or
                len(set(user.all_groups).intersection(self.can_edit_groups.all())))
