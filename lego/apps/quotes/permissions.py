from lego.apps.permissions import register
from lego.apps.permissions.index import PermissionIndex
from lego.apps.quotes.models import Quote


class QuotePermissionIndex(PermissionIndex):

    queryset = Quote.objects.all()

    list = ['/sudo/admin/quotes/list/']
    retrieve = []
    create = ['/sudo/admin/quotes/create/']
    update = ['/sudo/admin/quotes/update/']
    destroy = ['/sudo/admin/quotes/destroy/']

    approve = ['/sudo/admin/quotes/change-approval/']
    unapprove = ['/sudo/admin/quotes/change-approval/']


register(QuotePermissionIndex)
