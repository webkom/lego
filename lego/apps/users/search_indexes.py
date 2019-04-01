from django.db.models import Q, Value, F
from django.db.models.functions import Concat

from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import AbakusGroup, User
from .serializers.users import SearchGroupSerializer, SearchUserSerializer


class UserIndex(SearchIndex):

    queryset = User.objects.all()
    serializer_class = SearchUserSerializer
    result_fields = (
        "username",
        "first_name",
        "last_name",
        "full_name",
        "profile_picture",
    )
    autocomplete_result_fields = ("username", "full_name", "profile_picture")

    def get_autocomplete(self, instance):
        return [
            instance.username,
            instance.full_name,
            instance.last_name,
            instance.first_name,
        ]

    def autocomplete(self, query):
        return self.queryset\
            .annotate(fullname=Concat(F('first_name'), Value(' '), F('last_name')))\
            .filter(
                Q(first_name__istartswith=query) |
                Q(last_name__istartswith=query) |
                Q(username__istartswith=query) |
                Q(fullname__istartswith=query)
            )


register(UserIndex)


class GroupIndex(SearchIndex):

    queryset = AbakusGroup.objects.all()
    serializer_class = SearchGroupSerializer
    result_fields = ("name", "type", "logo")
    autocomplete_result_fields = ("name", "type")  # , "logo")

    def get_autocomplete(self, instance):
        return [instance.name] + instance.name.split(" ")

    def autocomplete(self, query):
        return self.queryset.filter(name__icontains=query)


register(GroupIndex)
