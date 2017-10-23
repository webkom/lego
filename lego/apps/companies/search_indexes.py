from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Company, CompanyContact
from .serializers import CompanySearchSerializer, CompanyContactSearchSerializer


class CompanyModelIndex(SearchIndex):

    queryset = Company.objects.all()
    serializer_class = CompanySearchSerializer
    result_fields = ('name', )
    autocomplete_result_fields = ('name', )

    def get_autocomplete(self, instance):
        return instance.name


register(CompanyModelIndex)


class CompanyContactModelIndex(SearchIndex):

    queryset = CompanyContact.objects.all()
    serializer_class = CompanyContactSearchSerializer
    result_fields = ('name', )
    autocomplete_result_fields = ('name', 'company')

    def get_autocomplete(self, instance):
        return instance.name


register(CompanyContactModelIndex)
