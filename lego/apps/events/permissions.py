from structlog import get_logger

from lego.apps.events.models import Event
from lego.apps.permissions import register
from lego.apps.permissions.index import PermissionIndex
from lego.apps.permissions.permissions import AbakusPermission

log = get_logger()


class EventPermissionIndex(PermissionIndex):

    queryset = Event.objects.all()

    list = ['/sudo/admin/events/list/']
    retrieve = ['/sudo/admin/events/retrieve/']
    create = ['/sudo/admin/events/create/']
    update = ['/sudo/admin/events/update/']
    destroy = ['/sudo/admin/events/destroy/']
    payment = ['/sudo/admin/events/payment/']

    safe_methods = ['list', 'retrieve', 'payment']


register(EventPermissionIndex)


class NestedEventPermissions(AbakusPermission):
    def has_object_permission(self, request, view, obj):
        obj = obj.event
        return super().has_object_permission(request, view, obj)
