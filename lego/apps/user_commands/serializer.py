from lego.apps.user_commands.models import UserCommand
from lego.utils.serializers import BasisModelSerializer


class UserCommandSerializer(BasisModelSerializer):
    class Meta:
        model = UserCommand
        fields = ("command_id", "pinned_position", "usage_count", "last_used")
