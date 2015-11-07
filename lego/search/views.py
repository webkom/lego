from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class AutocompleteViewSet(ViewSet):

    def list(self, request):
        query = request.GET.get('q')
        if not query:
            return Response([])

        queryset = SearchQuerySet().autocomplete(auto_complete=query)[:6]
        result = [{
            'verbose_name': result.verbose_name,
            'pk': result.pk,
            'content_type': result.content_type(),
            'title': result.title or result.autocomplete
        } for result in queryset]

        return Response(result)


class SearchViewSet(ViewSet):

    def list(self, request):
        query = request.GET.get('q')
        if not query:
            return Response([])

        queryset = SearchQuerySet().filter(search_text=AutoQuery(query)).highlight().facet('author')
        result = [{
            'verbose_name': result.verbose_name,
            'pk': result.pk,
            'content_type': result.content_type(),
            'title': result.title or result.autocomplete,
            'text': result.highlighted
        } for result in queryset]

        return Response({
            'results': result,
            'facet': queryset.facet_counts()['fields']
        })
