from django.db import transaction
from rest_framework import serializers

from rest_framework_jwt.serializers import ImpersonateAuthTokenSerializer

from lego.apps.events import constants
from lego.apps.events.fields import (
    PersonalConsentField,
    PersonalFeedbackField,
    PersonalPaymentStatusField,
    PersonalPresenceField,
    PhotoConsentField,
    PresenceField,
    SetPaymentStatusField,
)
from lego.apps.events.models import Pool, Registration
from lego.apps.users.models import User as user_model
from lego.apps.users.serializers.users import (
    AdministrateUserExportSerializer,
    AdministrateUserSerializer,
    PublicUserSerializer,
)
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer

User: user_model = ImpersonateAuthTokenSerializer.User


class AdminUnregisterSerializer(serializers.Serializer):
    user = PrimaryKeyRelatedFieldNoPKOpt(queryset=User.objects.all())
    admin_unregistration_reason = serializers.CharField(required=True)


class AdminRegistrationCreateAndUpdateSerializer(serializers.Serializer):
    user = PrimaryKeyRelatedFieldNoPKOpt(queryset=User.objects.all())
    pool = PrimaryKeyRelatedFieldNoPKOpt(queryset=Pool.objects.all(), required=False)
    feedback = serializers.CharField(
        required=False,
        max_length=Registration._meta.get_field("feedback").max_length or 255,
    )
    admin_registration_reason = serializers.CharField(
        max_length=(
            Registration._meta.get_field("admin_registration_reason").max_length or 255
        ),
        required=True,
    )


class RegistrationCreateAndUpdateSerializer(BasisModelSerializer):
    captcha_response = serializers.CharField(required=False)
    payment_status = SetPaymentStatusField(
        required=False, choices=constants.PAYMENT_STATUS_CHOICES
    )
    presence = PresenceField(required=False, choices=constants.PRESENCE_CHOICES)

    class Meta:
        model = Registration
        fields = (
            "id",
            "feedback",
            "presence",
            "captcha_response",
            "payment_status",
        )

    def update(self, instance, validated_data):
        with transaction.atomic():
            presence = validated_data.pop("presence", None)
            super().update(instance, validated_data)
            if presence:
                instance.set_presence(presence)

            return instance


class RegistrationAnonymizedReadSerializer(BasisModelSerializer):
    class Meta:
        model = Registration
        fields = ("id", "pool", "status")
        read_only = True


class RegistrationPublicReadSerializer(BasisModelSerializer):
    user = PublicUserSerializer()

    class Meta:
        model = Registration
        fields = ("id", "user", "pool", "status")
        read_only = True


class RegistrationReadSerializer(RegistrationPublicReadSerializer):
    feedback = PersonalFeedbackField()
    presence = PersonalPresenceField()
    LEGACY_photo_consent = PersonalConsentField()
    shared_memberships = serializers.IntegerField(required=False)

    class Meta(RegistrationPublicReadSerializer.Meta):
        fields = RegistrationPublicReadSerializer.Meta.fields + (  # type: ignore
            "feedback",
            "shared_memberships",
            "presence",
            "LEGACY_photo_consent",
            "status",
            "event",
        )


class RegistrationSearchReadSerializer(RegistrationPublicReadSerializer):
    class Meta(RegistrationPublicReadSerializer.Meta):
        fields = RegistrationPublicReadSerializer.Meta.fields + (  # type: ignore
            "presence",
            "LEGACY_photo_consent",
        )


class RegistrationSearchSerializer(serializers.Serializer):
    username = serializers.CharField()


class RegistrationConsentSerializer(serializers.Serializer):
    username = serializers.CharField()
    LEGACY_photo_consent = serializers.CharField()


class RegistrationPaymentReadSerializer(RegistrationReadSerializer):
    payment_status = PersonalPaymentStatusField()

    class Meta(RegistrationReadSerializer.Meta):
        fields = RegistrationReadSerializer.Meta.fields + ("payment_status",)  # type: ignore


class RegistrationReadDetailedSerializer(BasisModelSerializer):
    user = AdministrateUserSerializer()
    photo_consents = PhotoConsentField()

    class Meta:
        model = Registration
        fields = (
            "id",
            "user",
            "created_by",
            "updated_by",
            "pool",
            "event",
            "presence",
            "feedback",
            "status",
            "registration_date",
            "unregistration_date",
            "admin_registration_reason",
            "payment_intent_id",
            "payment_status",
            "payment_amount",
            "payment_amount_refunded",
            "LEGACY_photo_consent",
            "photo_consents",
        )
        read_only = True


class RegistrationReadDetailedExportSerializer(RegistrationReadDetailedSerializer):
    user = AdministrateUserExportSerializer()  # type: ignore


class StripeMetaSerializer(serializers.Serializer):
    EVENT_ID = serializers.IntegerField()
    USER_ID = serializers.IntegerField()
    USER = serializers.CharField()
    EMAIL = serializers.EmailField()


class StripePaymentIntentErrorSerializer(serializers.Serializer):
    """
    Stripe payment intent last error.
    https://stripe.com/docs/api/payment_intents/object#payment_intent_object-last_payment_error
    """

    code = serializers.CharField()
    doc_url = serializers.CharField()
    message = serializers.CharField()
    type = serializers.CharField()


class StripePaymentIntentSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount = serializers.IntegerField()
    status = serializers.CharField()
    metadata = StripeMetaSerializer()
    last_payment_error = StripePaymentIntentErrorSerializer(allow_null=True)


class StripeChargeSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount = serializers.IntegerField()
    amount_refunded = serializers.IntegerField()
    status = serializers.CharField()
    metadata = StripeMetaSerializer()
