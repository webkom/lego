from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import User
from .serializers.users import PublicUserSerializer


class UserIndex(SearchIndex):

    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    result_fields = ('username', 'first_name', 'last_name', 'full_name', 'picture')
    autocomplete_result_fields = ('full_name', 'picture')

    def get_autocomplete(self, instance):
        return [instance.username, instance.full_name]


register(UserIndex)
