from django.db.models import Q

from lego.utils.managers import PersistentModelManager



class EventManager(PersistentModelManager):

    def filtered_event_list(self, user):
        queryset = super().get_queryset()
        to_remove = []
        for event in queryset.all():
            if not event.public:
                if not event.event_visible_to_user(user):
                    to_remove.append(event)
        for event in to_remove:
            queryset = queryset.exclude(id=event.id)
        return queryset
