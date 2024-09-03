from lego.apps.files.fields import ImageField
from lego.apps.lending.models import LendableObject
from lego.utils.serializers import (
    BasisModelSerializer,
    ObjectPermissionsSerializerMixin,
)


class LendableObjectSerializer(BasisModelSerializer):
    image = ImageField(required=False, options={"height": 500})

    class Meta:
        model = LendableObject
        fields = (
            "id",
            "title",
            "description",
            "image",
            "location",
        )


class LendableObjectAdminSerializer(
    ObjectPermissionsSerializerMixin, LendableObjectSerializer
):
    class Meta(LendableObjectSerializer.Meta):
        fields = (
            LendableObjectSerializer.Meta.fields
            + ObjectPermissionsSerializerMixin.Meta.fields
        )
