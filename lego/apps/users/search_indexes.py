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

    autocomplete_fields = ("first_name", "last_name", "username")
    fallback_to_autocomplete = True

    def get_autocomplete(self, instance):
        return [
            instance.username,
            instance.full_name,
            instance.last_name,
            instance.first_name,
        ]


register(UserIndex)


class GroupIndex(SearchIndex):

    queryset = AbakusGroup.objects.all()
    serializer_class = SearchGroupSerializer
    result_fields = ("name", "type", "logo")
    autocomplete_result_fields = ("name", "type", "logo")

    autocomplete_fields = ("name",)
    fallback_to_autocomplete = True

    def get_autocomplete(self, instance):
        return [instance.name] + instance.name.split(" ")


register(GroupIndex)
