from django.contrib.auth.models import UserManager
from django.db.models import Q
from django.utils import timezone
from mptt.managers import TreeManager

from lego.utils.managers import PersistentModelManager


class AbakusGroupManager(TreeManager, PersistentModelManager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class AbakusGroupManagerWithoutText(AbakusGroupManager):
    def get_queryset(self, *args, **kwargs):
            return super().get_queryset().defer('text')


class AbakusUserManager(UserManager, PersistentModelManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        We do not set is_staff or is_superuser as they are a @cached_property
        in our User model.
        """
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        """
        We do not set is_staff or is_superuser as they are a @cached_property
        in our User model.
        """
        return self._create_user(username, email, password, **extra_fields)

    def get_by_natural_key(self, username):
        return self.get(Q(username__iexact=username.lower()) | Q(email__iexact=username.lower()))


class MembershipManager(PersistentModelManager):
    def get_by_natural_key(self, username, abakus_group_name):
        return self.get(user__username__iexact=username.lower(),
                        abakus_group__name__iexact=abakus_group_name.lower())


class UserPenaltyManager(PersistentModelManager):

    def valid(self):
        from lego.apps.users.models import Penalty
        offset = Penalty.penalty_offset(timezone.now(), False)
        return super().filter(created_at__gt=timezone.now() - offset)
