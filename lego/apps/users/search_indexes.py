from lego.apps.search import register
from lego.apps.search.index import SearchIndex

from .models import User
from .serializers import PublicUserSerializer


class UserIndex(SearchIndex):
    model = User
    serializer_class = PublicUserSerializer
    autocomplete_fields = ['full_name']

    def get_autocomplete(self, instance):
        return [instance.username, instance.full_name]


register(UserIndex)
