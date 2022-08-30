from rest_framework import serializers

from lego.apps.users.models import PhotoConsent


class PhotoConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoConsent
        fields = ("user", "year", "semester", "domain", "is_consenting", "updated_at")
