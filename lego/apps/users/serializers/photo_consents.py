from lego.apps.users.models import PhotoConsent
from lego.utils.serializers import BasisModelSerializer


class PhotoConsentSerializer(BasisModelSerializer):
    class Meta:
        model = PhotoConsent
        fields = (
            "user",
            "year",
            "semester",
            "domain",
            "is_consenting",
            "updated_at",
        )

    def __init__(self, instance=None, **kwargs):
        data = kwargs.get("data", None)
        if data:
            user = data.get("user", None)
            year = data.get("year", None)
            semester = data.get("semester", None)
            domain = data.get("domain", None)

            try:
                instance = PhotoConsent.objects.get(
                    user=user, year=year, semester=semester, domain=domain
                )
            except PhotoConsent.DoesNotExist:
                pass

        super().__init__(instance, **kwargs)
