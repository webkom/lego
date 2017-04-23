from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import User
from .serializers.users import SearchUserSerializer


class UserIndex(SearchIndex):

    queryset = User.objects.all()
    serializer_class = SearchUserSerializer
    result_fields = ('username', 'first_name', 'last_name', 'full_name', 'profile_picture')
    autocomplete_result_fields = ('username', 'full_name', 'profile_picture')

    def get_autocomplete(self, instance):
        return [instance.username, instance.full_name, instance.last_name, instance.first_name]


register(UserIndex)
