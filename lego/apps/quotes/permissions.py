from lego.apps.permissions import register
from lego.apps.permissions.index import PermissionIndex
from lego.apps.quotes.models import Quote


class QuotePermissionIndex(PermissionIndex):

    queryset = Quote.objects.all()

    list = (['/sudo/admin/quotes/list/'], 'can_view')
    retrieve = ([], None)
    create = (['/sudo/admin/quotes/create/'], None)
    update = (['/sudo/admin/quotes/update/'], 'can_edit')
    destroy = (['/sudo/admin/quotes/destroy/'], 'can_edit')

    approve = (['/sudo/admin/quotes/change-approval/'], 'can_edit')
    unapprove = (['/sudo/admin/quotes/change-approval/'], 'can_edit')


register(QuotePermissionIndex)
