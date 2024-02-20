from lego.utils.managers import PersistentModelManager


class LendingInstanceManager(PersistentModelManager):
    def create(self, *args, **kwargs):
        from lego.apps.users.models import Membership, User
        from lego.apps.lending.notifications import LendingInstanceNotification

        lending_instance = super().create(*args, **kwargs)
        abakus_groups = lending_instance.lendable_object.responsible_groups.all()
        role = lending_instance.lendable_object.responsible_role
        if role:
            users_to_be_notified = Membership.objects.filter(
                abakus_group__in=abakus_groups, role=role
            ).values_list("user", flat=True)
        else:
            users_to_be_notified = Membership.objects.filter(
                abakus_group__in=abakus_groups
            ).values_list("user", flat=True)
        for user_id in users_to_be_notified:
            user = User.objects.get(pk=user_id)
            notification = LendingInstanceNotification(
                lending_instance=lending_instance,
                user=user,
            )
            notification.notify()

        return lending_instance
