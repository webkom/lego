from django.utils import timezone

from lego.utils.managers import PersistentModelManager


class AbakusGroupManager(PersistentModelManager):
    def get_by_natural_key(self, name):
        return self.get(name__iexact=name.lower())


class UserManager(PersistentModelManager):
    def get_by_natural_key(self, username):
        return self.get(username__iexact=username.lower())


class MembershipManager(PersistentModelManager):
    def get_by_natural_key(self, username, abakus_group_name):
        return self.get(user__username__iexact=username.lower(),
                        abakus_group__name__iexact=abakus_group_name.lower())


class UserPenaltyManager(PersistentModelManager):

    def valid(self):
        from lego.apps.users.models import Penalty
        offset = Penalty.penalty_offset(timezone.now(), False)
        return super(UserPenaltyManager, self).get_queryset().\
            filter(created_at__gt=timezone.now() - offset)
