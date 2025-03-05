from lego.apps.banners.models import Banners
from lego.utils.serializers import BasisModelSerializer


class BannersSerializer(BasisModelSerializer):
    class Meta:
        model = Banners
        fields = (
            "id",
            "header",
            "subheader",
            "link",
            "current_private",
            "current_public",
        )

    def update(self, instance, validated_data):
        if validated_data.get("current_private", False):
            Banners.objects.exclude(pk=instance.pk).update(current_private=False)
        if validated_data.get("current_public", False):
            Banners.objects.exclude(pk=instance.pk).update(current_public=False)
        return super().update(instance, validated_data)

    def create(self, validated_data):
        if validated_data.get("current_private", False):
            Banners.objects.all().update(current_private=False)
        if validated_data.get("current_public", False):
            Banners.objects.all().update(current_private=False)
        return super().create(validated_data)
