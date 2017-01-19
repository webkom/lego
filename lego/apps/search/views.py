from rest_framework import permissions, viewsets
from rest_framework.response import Response

from .search import autocomplete, search
from .serializers import AutocompleteSerializer, QuerySerializer


class SearchViewSet(viewsets.ViewSet):
    """
    Post { 'query': query, 'types': [content_type], 'filters': { event_type: ['party', 'course']} }
    to this endpoint.

    types and filters is optional.
    """
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = QuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(list(search(user=self.request.user, **serializer.data)))


class AutocompleteViewSet(viewsets.ViewSet):
    """
    Post { 'query': query, 'types': [content_type] } to this endpoint.

    types is optional.
    """
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = AutocompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(list(autocomplete(user=self.request.user, **serializer.data)))
