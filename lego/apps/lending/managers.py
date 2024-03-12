from lego.utils.managers import BasisModelManager


class LendingInstanceManager(BasisModelManager):
    def create(self, *args, **kwargs):
        from lego.apps.users.models import Membership, User
        from lego.apps.lending.notifications import LendingInstanceNotification

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
            notification = LendingInstanceNotification(
                lending_instance=lending_instance,
                user=user,
            )
            notification.notify()

        return lending_instance
    
    #TODO: We probably need another template for accepting instances
    def update(self, *args, **kwargs):
        from lego.apps.lending.notifications import LendingInstanceNotification

        lending_instance = super().update(*args, **kwargs)
        notification = LendingInstanceNotification(
            lending_instance=lending_instance,
            user=lending_instance.created_by,
        )
        notification.notify()

        return lending_instance


    def get_queryset(self):
        return super().get_queryset().select_related("created_by")

