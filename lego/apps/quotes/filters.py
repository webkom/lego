from django_filters import FilterSet

from lego.apps.permissions.filters import AbakusObjectPermissionFilter

from .models import Quote


class QuotesFilterSet(FilterSet):

    class Meta:
        model = Quote
        fields = ('approved', )


class QuoteModelFilter(AbakusObjectPermissionFilter):

    def filter_queryset(self, request, queryset, view):
        access_unapproved = False
        queryset = super().filter_queryset(request, queryset, view)

        if request.user and request.user.is_authenticated:
            access_unapproved = request.user.has_perm('quotes.quote.approve')

        if not access_unapproved:
            return queryset.filter(approved=True)
        return queryset
