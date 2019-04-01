from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import BooleanField, CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.fields import CompanyField
from lego.apps.companies.models import Company
from lego.apps.content.fields import ContentSerializerField
from lego.apps.events import constants
from lego.apps.events.constants import PRESENT
from lego.apps.events.fields import ActivationTimeField, IsAdmittedField, SpotsLeftField
from lego.apps.events.models import Event, Pool
from lego.apps.events.serializers.pools import (
    PoolAdministrateExportSerializer,
    PoolAdministrateSerializer,
    PoolCreateAndUpdateSerializer,
    PoolReadAuthSerializer,
    PoolReadSerializer,
)
from lego.apps.events.serializers.registrations import (
    RegistrationReadDetailedExportSerializer,
    RegistrationReadDetailedSerializer,
    RegistrationReadSerializer,
)
from lego.apps.files.fields import ImageField
from lego.apps.tags.serializers import TagSerializerMixin
from lego.apps.users.constants import GROUP_GRADE
from lego.apps.users.fields import AbakusGroupField
from lego.apps.users.models import AbakusGroup
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class EventPublicSerializer(BasisModelSerializer):

    thumbnail = ImageField(
        source="cover",
        required=False,
        options={"height": 500, "width": 500, "smart": True},
    )

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "event_type",
            "event_status_type",
            "location",
            "thumbnail",
        )
        read_only = True


class EventReadSerializer(TagSerializerMixin, BasisModelSerializer):
    company = CompanyField(queryset=Company.objects.all())
    cover = ImageField(required=False, options={"height": 500})
    thumbnail = ImageField(
        source="cover",
        required=False,
        options={"height": 500, "width": 500, "smart": True},
    )
    activation_time = ActivationTimeField()
    is_admitted = IsAdmittedField()

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "cover",
            "event_type",
            "event_status_type",
            "location",
            "start_time",
            "end_time",
            "thumbnail",
            "total_capacity",
            "company",
            "registration_count",
            "tags",
            "activation_time",
            "is_admitted",
            "survey",
        )
        read_only = True


class EventReadDetailedSerializer(TagSerializerMixin, BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    content_target = CharField(read_only=True)
    cover = ImageField(required=False, options={"height": 500})
    company = CompanyField(queryset=Company.objects.all())
    responsible_group = AbakusGroupField(
        queryset=AbakusGroup.objects.all(), required=False, allow_null=True
    )
    pools = PoolReadSerializer(many=True)
    active_capacity = serializers.ReadOnlyField()
    text = ContentSerializerField()
    created_by = PublicUserSerializer()

    registration_close_time = serializers.DateTimeField(read_only=True)
    unregistration_close_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "cover",
            "text",
            "event_type",
            "event_status_type",
            "location",
            "comments",
            "content_target",
            "start_time",
            "end_time",
            "merge_time",
            "pools",
            "registration_close_time",
            "registration_deadline_hours",
            "unregistration_close_time",
            "unregistration_deadline",
            "unregistration_deadline_hours",
            "company",
            "responsible_group",
            "active_capacity",
            "feedback_description",
            "feedback_required",
            "is_priced",
            "price_member",
            "price_guest",
            "use_stripe",
            "payment_due_date",
            "use_captcha",
            "waiting_registration_count",
            "tags",
            "is_merged",
            "heed_penalties",
            "created_by",
            "is_abakom_only",
            "registration_count",
            "legacy_registration_count",
            "survey",
            "use_consent",
            "youtube_url",
            "use_contact_tracing",
            "mazemap_poi",
        )
        read_only = True


class EventForSurveySerializer(EventReadSerializer):
    attended_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = EventReadSerializer.Meta.fields + (
            "registration_count",
            "waiting_registration_count",
            "attended_count",
        )
        read_only = True

    def get_attended_count(self, event):
        return event.registrations.filter(presence=PRESENT).count()


class EventUserRegSerializer(EventReadSerializer):
    user_reg = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = EventReadSerializer.Meta.fields + ("user_reg",)
        read_only = True

    def get_user_reg(self, event):
        return RegistrationReadSerializer(event.user_reg[0]).data


class EventReadUserDetailedSerializer(EventReadDetailedSerializer):
    """User specfic event serializer that appends data based on request.user"""

    activation_time = ActivationTimeField()
    is_admitted = IsAdmittedField()
    spots_left = SpotsLeftField()
    price = serializers.SerializerMethodField()

    class Meta(EventReadDetailedSerializer.Meta):
        fields = EventReadDetailedSerializer.Meta.fields + (
            "price",
            "activation_time",
            "is_admitted",
            "spots_left",
        )

    def get_price(self, obj):
        request = self.context.get("request", None)
        if request:
            return obj.get_price(user=request.user)


class EventReadAuthUserDetailedSerializer(EventReadUserDetailedSerializer):
    pools = PoolReadAuthSerializer(many=True)
    waiting_registrations = RegistrationReadSerializer(many=True)
    unanswered_surveys = serializers.SerializerMethodField()

    class Meta(EventReadUserDetailedSerializer.Meta):
        fields = EventReadUserDetailedSerializer.Meta.fields + (
            "waiting_registrations",
            "unanswered_surveys",
        )

    def get_unanswered_surveys(self, obj):
        request = self.context.get("request", None)
        return request.user.unanswered_surveys()


class EventAdministrateSerializer(EventReadSerializer):
    pools = PoolAdministrateSerializer(many=True)
    unregistered = RegistrationReadDetailedSerializer(many=True)
    waiting_registrations = RegistrationReadDetailedSerializer(many=True)

    class Meta(EventReadSerializer.Meta):
        fields = EventReadSerializer.Meta.fields + (
            "pools",
            "unregistered",
            "waiting_registrations",
            "use_consent",
            "use_contact_tracing",
            "created_by",
        )


class EventAdministrateExportSerializer(EventAdministrateSerializer):
    pools = PoolAdministrateExportSerializer(many=True)
    unregistered = RegistrationReadDetailedExportSerializer(many=True)
    waiting_registrations = RegistrationReadDetailedExportSerializer(many=True)


class EventCreateAndUpdateSerializer(TagSerializerMixin, BasisModelSerializer):
    cover = ImageField(required=False, options={"height": 500})
    responsible_group = AbakusGroupField(
        queryset=AbakusGroup.objects.all(), required=False, allow_null=True
    )
    pools = PoolCreateAndUpdateSerializer(many=True, required=False)
    text = ContentSerializerField()
    is_abakom_only = BooleanField(required=False, default=False)

    registration_close_time = serializers.DateTimeField(read_only=True)
    unregistration_close_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "cover",
            "description",
            "text",
            "company",
            "responsible_group",
            "feedback_description",
            "feedback_required",
            "event_type",
            "event_status_type",
            "location",
            "is_priced",
            "price_member",
            "price_guest",
            "use_stripe",
            "payment_due_date",
            "start_time",
            "end_time",
            "merge_time",
            "use_captcha",
            "tags",
            "pools",
            "unregistration_deadline",
            "unregistration_deadline_hours",
            "pinned",
            "use_consent",
            "heed_penalties",
            "is_abakom_only",
            "registration_deadline_hours",
            "registration_close_time",
            "unregistration_close_time",
            "youtube_url",
            "use_contact_tracing",
        )

    def validate(self, data):
        """
        Check that start is before finish.
        """
        if hasattr(data, "start_time") and hasattr(data, "end_time"):
            if data["start_time"] > data["end_time"]:
                raise serializers.ValidationError(
                    {
                        "end_time": "User does not have the required permissions for time travel"
                    }
                )
        if (
            self.instance is not None
            and "use_contact_tracing" in data
            and data["use_contact_tracing"] != self.instance.use_contact_tracing
            and self.instance.registrations.exists()
        ):
            raise serializers.ValidationError(
                {
                    "use_contact_tracing": "Cannot change this field after registration has started"
                }
            )

        return data

    def create(self, validated_data):
        pools = validated_data.pop("pools", [])
        is_abakom_only = validated_data.pop("is_abakom_only", False)
        event_status_type = validated_data.get(
            "event_status_type", Event._meta.get_field("event_status_type").default
        )
        if event_status_type == constants.TBA:
            pools = []
            validated_data["location"] = "TBA"
        elif event_status_type == constants.OPEN:
            pools = []
        elif event_status_type == constants.INFINITE:
            pools = [pools[0]]
            pools[0]["capacity"] = 0
        with transaction.atomic():
            event = super().create(validated_data)
            for pool in pools:
                permission_groups = pool.pop("permission_groups")
                created_pool = Pool.objects.create(event=event, **pool)
                created_pool.permission_groups.set(permission_groups)
            event.set_abakom_only(is_abakom_only)
            return event

    def update(self, instance, validated_data):
        pools = validated_data.pop("pools", None)
        is_abakom_only = validated_data.pop("is_abakom_only", False)
        event_status_type = validated_data.get(
            "event_status_type", Event._meta.get_field("event_status_type").default
        )
        if event_status_type == constants.TBA:
            pools = []
            validated_data["location"] = "TBA"
        elif event_status_type == constants.OPEN:
            pools = []
        elif event_status_type == constants.INFINITE:
            pools = [pools[0]]
            pools[0]["capacity"] = 0
        with transaction.atomic():
            if pools is not None:
                existing_pools = list(instance.pools.all().values_list("id", flat=True))
                for pool in pools:
                    pool_id = pool.get("id", None)
                    if pool_id in existing_pools:
                        existing_pools.remove(pool_id)
                    permission_groups = pool.pop("permission_groups")
                    created_pool = Pool.objects.update_or_create(
                        event=instance,
                        id=pool_id,
                        defaults={
                            "name": pool.get("name"),
                            "capacity": pool.get("capacity", 0),
                            "activation_date": pool.get("activation_date"),
                        },
                    )[0]
                    created_pool.permission_groups.set(permission_groups)
                for pool_id in existing_pools:
                    Pool.objects.get(id=pool_id).delete()
            instance.set_abakom_only(is_abakom_only)
            return super().update(instance, validated_data)


class FrontpageEventSerializer(serializers.ModelSerializer):
    cover = ImageField(required=False, options={"height": 500})
    thumbnail = ImageField(
        source="cover",
        required=False,
        options={"height": 500, "width": 500, "smart": True},
    )
    text = ContentSerializerField()
    activation_time = ActivationTimeField()
    is_admitted = IsAdmittedField()

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "cover",
            "text",
            "event_type",
            "event_status_type",
            "location",
            "start_time",
            "thumbnail",
            "end_time",
            "total_capacity",
            "company",
            "registration_count",
            "tags",
            "activation_time",
            "is_admitted",
            "pinned",
        )
        read_only = True


class EventSearchSerializer(serializers.ModelSerializer):
    cover = ImageField(required=False, options={"height": 500})
    text = ContentSerializerField()

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "description",
            "text",
            "cover",
            "location",
            "start_time",
            "end_time",
        )
        read_only = True


def populate_event_registration_users_with_grade(event_dict):
    """
    Populates every user in registrations in a serialized event with `grade`.
    Mainly used in the administrate endpoint
    :param event_dict:
    :return:
    """
    grades = AbakusGroup.objects.filter(type=GROUP_GRADE).values("id", "name")
    grade_dict = {item["id"]: item for item in grades}
    for pool in event_dict.get("pools", []):
        for registration in pool.get("registrations", []):
            user = registration.get("user", {})
            abakus_groups = user.get("abakus_groups", [])
            user["grade"] = None
            for id in abakus_groups:
                grade = grade_dict.get(id, None)
                if grade:
                    user["grade"] = grade
    return event_dict
