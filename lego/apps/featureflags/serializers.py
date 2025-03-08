from rest_framework import serializers

from lego.apps.featureflags.models import FeatureFlag
from lego.apps.users.fields import AbakusGroupField
from lego.apps.users.models import AbakusGroup
from lego.utils.serializers import BasisModelSerializer


class FeatureFlagAdminSerializer(BasisModelSerializer):
    display_groups = AbakusGroupField(
        queryset=AbakusGroup.objects.all(), allow_null=True, required=False, many=True
    )
    can_see_flag = serializers.SerializerMethodField(read_only=True)

    def get_can_see_flag(self, obj: FeatureFlag):
        return obj.can_see_flag(self.context["request"].user)

    class Meta:
        model = FeatureFlag
        fields = (
            "id",
            "identifier",
            "display_groups",
            "is_active",
            "percentage",
            "can_see_flag",
        )


class FeatureFlagPublicSerializer(BasisModelSerializer):

    can_see_flag = serializers.SerializerMethodField(read_only=True)

    def get_can_see_flag(self, obj: FeatureFlag):
        return obj.can_see_flag(self.context["request"].user)

    class Meta:
        model = FeatureFlag
        fields = ("id", "identifier", "can_see_flag")
