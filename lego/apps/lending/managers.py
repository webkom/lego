from lego.utils.managers import BasisModelManager


class LendingInstanceManager(BasisModelManager):
    def create(self, *args, **kwargs):
        from lego.apps.lending.notifications import LendingInstanceCreateNotification
        from lego.apps.users.models import Membership, User

        lending_instance = super().create(*args, **kwargs)
        abakus_groups = lending_instance.lendable_object.responsible_groups.all()
        roles = lending_instance.lendable_object.responsible_roles
        if roles:
            users_to_be_notified = Membership.objects.filter(
                abakus_group__in=abakus_groups, role__in=roles
            ).values_list("user", flat=True)
        else:
            users_to_be_notified = Membership.objects.filter(
                abakus_group__in=abakus_groups
            ).values_list("user", flat=True)
        for user_id in users_to_be_notified:
            user = User.objects.get(pk=user_id)
            notification = LendingInstanceCreateNotification(
                lending_instance=lending_instance,
                user=user,
            )
            notification.notify()

        return lending_instance

    def get_queryset(self):
        return super().get_queryset().select_related("created_by")
