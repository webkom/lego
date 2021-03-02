from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import F, Q, Value
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
        return self.queryset.annotate(
            search=SearchVector("first_name", "last_name", "username")
        ).filter(
            search=SearchQuery(
                ":* & ".join(query.split() + [""]).strip("& ").strip(),
                search_type="raw",
            )
        )


register(UserIndex)


class GroupIndex(SearchIndex):

    queryset = AbakusGroup.objects.all()
    serializer_class = SearchGroupSerializer
    result_fields = ("name", "type", "logo")
    autocomplete_result_fields = ("name", "type", "logo")

    def get_autocomplete(self, instance):
        return [instance.name] + instance.name.split(" ")

    def autocomplete(self, query):
        return self.queryset.annotate(search=SearchVector("name")).filter(
            search=SearchQuery(
                ":* & ".join(query.split() + [""]).strip("& ").strip(),
                search_type="raw",
            )
        )


register(GroupIndex)
