from rest_framework import permissions, viewsets
from rest_framework.response import Response

from .search import autocomplete, search
from .serializers import QuerySerializer


class SearchViewSet(viewsets.GenericViewSet):

    permission_classes = [permissions.AllowAny]
    serializer_class = QuerySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.data['query']

        return Response(search(query, self.request.user))


class AutocompleteViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = QuerySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        query = serializer.data['query']

        return Response(autocomplete(query, self.request.user))
