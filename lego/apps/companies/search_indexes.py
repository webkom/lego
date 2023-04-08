from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import Company
from .serializers import CompanySearchSerializer


class CompanyModelIndex(SearchIndex):
    queryset = Company.objects.all()
    serializer_class = CompanySearchSerializer
    result_fields = ("name", "description")
    autocomplete_result_fields = ("name",)

    search_fields = ("name", "description")
    autocomplete_fields = ("name",)

    def get_autocomplete(self, instance):
        return instance.name


register(CompanyModelIndex)
