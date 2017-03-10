from django.utils import timezone
from mptt.managers import TreeManager

from lego.utils.managers import PersistentModelManager


class AbakusGroupManager(TreeManager, PersistentModelManager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class UserManager(PersistentModelManager):
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username.lower())

    def create_user(self, *args, **kwargs):
        # Initialize the User object.
        new_user = self.model(**kwargs)

        # The password is in plaintext, we need to encode it.
        new_user.set_password(kwargs['password'])

        # Save the User object and return it.
        new_user.save()
        return new_user


class MembershipManager(PersistentModelManager):
    def get_by_natural_key(self, username, abakus_group_name):
        return self.get(user__username__iexact=username.lower(),
                        abakus_group__name__iexact=abakus_group_name.lower())


class UserPenaltyManager(PersistentModelManager):

    def valid(self):
        from lego.apps.users.models import Penalty
        offset = Penalty.penalty_offset(timezone.now(), False)
        return super().filter(created_at__gt=timezone.now() - offset)
