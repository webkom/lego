from lego.apps.user_commands.models import UserCommand
from lego.utils.serializers import BasisModelSerializer


class UserCommandSerializer(BasisModelSerializer):
    class Meta:
        model = UserCommand
        fields = ("command_id", "position", "last_used")
