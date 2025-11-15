from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpRequest
from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers.comments import CommentSerializer
from lego.apps.companies.fields import CompanyField
from lego.apps.companies.models import Company
from lego.apps.content.fields import ContentSerializerField
from lego.apps.events import constants
from lego.apps.events.constants import PRESENCE_CHOICES
from lego.apps.events.fields import (
    ActivationTimeField,
    FollowingField,
    IsAdmittedField,
    RegistrationCountField,
    SpotsLeftField,
    TotalCapacityField,
)
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.events.serializers.pools import (
    PoolAdministrateAllergiesSerializer,
    PoolAdministrateSerializer,
    PoolCreateAndUpdateSerializer,
    PoolReadAuthSerializer,
    PoolReadSerializer,
)
from lego.apps.events.serializers.registrations import (
    RegistrationReadDetailedAllergiesSerializer,
    RegistrationReadDetailedSerializer,
    RegistrationReadSerializer,
)
from lego.apps.files.fields import File, ImageField
from lego.apps.tags.serializers import TagSerializerMixin
from lego.apps.users.constants import GROUP_GRADE
from lego.apps.users.fields import AbakusGroupField, PublicUserField
from lego.apps.users.models import AbakusGroup, PhotoConsent, User
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.photo_consents import PhotoConsentSerializer
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import (
    BasisModelSerializer,
    ObjectPermissionsSerializerMixin,
)


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
            "slug",
            "description",
            "event_type",
            "event_status_type",
            "location",
            "thumbnail",
        )
        read_only = True


class EventReadSerializer(
    TagSerializerMixin, BasisModelSerializer, ObjectPermissionsSerializerMixin
):
    company = CompanyField(queryset=Company.objects.all())
    cover = ImageField(required=False, options={"height": 500})
    cover_placeholder = ImageField(
        source="cover", required=False, options={"height": 50, "filters": ["blur(20)"]}
    )
    thumbnail = ImageField(
        source="cover",
        required=False,
        options={"height": 500, "width": 500, "smart": True},
    )
    activation_time = ActivationTimeField()
    is_admitted = IsAdmittedField()
    registration_count = RegistrationCountField()
    total_capacity = TotalCapacityField()
    user_reg = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "cover",
            "cover_placeholder",
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
            "is_priced",
            "is_foreign_language",
            "user_reg",
            "show_company_description",
        ) + ObjectPermissionsSerializerMixin.Meta.fields
        read_only = True

    def get_user_reg(self, event):
        if hasattr(event, "user_reg") and event.user_reg:
            return RegistrationReadSerializer(event.user_reg[0]).data
        return None


class EventReadDetailedSerializer(
    TagSerializerMixin, BasisModelSerializer, ObjectPermissionsSerializerMixin
):
    comments = CommentSerializer(read_only=True, many=True)
    content_target = CharField(read_only=True)
    cover = ImageField(required=False, options={"height": 500})
    cover_placeholder = ImageField(
        source="cover", required=False, options={"height": 50, "filters": ["blur(20)"]}
    )
    company = CompanyField(queryset=Company.objects.all())
    responsible_group = PublicAbakusGroupSerializer(read_only=True)
    pools = PoolReadSerializer(many=True)
    active_capacity = serializers.ReadOnlyField()
    text = ContentSerializerField()
    registration_close_time = serializers.DateTimeField(read_only=True)
    unregistration_close_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Event
        fields = ObjectPermissionsSerializerMixin.Meta.fields + (
            "id",
            "title",
            "slug",
            "description",
            "cover",
            "cover_placeholder",
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
            "tags",
            "is_merged",
            "heed_penalties",
            "legacy_registration_count",
            "survey",
            "use_consent",
            "youtube_url",
            "mazemap_poi",
            "is_foreign_language",
            "show_company_description",
        )
        read_only = True


class EventForSurveySerializer(EventReadSerializer):
    attended_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = EventReadSerializer.Meta.fields + ("attended_count",)
        read_only = True

    def get_attended_count(self, event):
        request = self.context.get("request", None)
        if request and request.user.is_authenticated:
            return event.registrations.filter(presence=PRESENCE_CHOICES.PRESENT).count()
        return None


class ImageGallerySerializer(BasisModelSerializer):
    cover = ImageField(source="key", required=True, options={"height": 500})
    cover_placeholder = ImageField(
        source="key", required=False, options={"height": 50, "filters": ["blur(20)"]}
    )

    class Meta:
        model = File
        fields = (
            "key",
            "file_type",
            "state",
            "public",
            "save_for_use",
            "cover",
            "token",
            "cover_placeholder",
        )
        read_only = True


class EventReadUserDetailedSerializer(EventReadDetailedSerializer):
    """User specific event serializer that appends data based on request.user"""

    activation_time = ActivationTimeField()
    is_admitted = IsAdmittedField()
    following = FollowingField()
    spots_left = SpotsLeftField()
    pending_registration = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    photo_consents = serializers.SerializerMethodField()

    class Meta(EventReadDetailedSerializer.Meta):
        fields = EventReadDetailedSerializer.Meta.fields + (  # type: ignore
            "price",
            "activation_time",
            "is_admitted",
            "following",
            "spots_left",
            "pending_registration",
            "photo_consents",
        )

    def get_price(self, obj):
        request: HttpRequest = self.context.get("request", None)
        if request:
            return obj.get_price(user=request.user)

    def get_pending_registration(self, obj):
        request: HttpRequest = self.context.get("request", None)
        if not request or not request.user.is_authenticated:
            return None

        try:
            reg = Registration.objects.get(
                event_id=obj.id,
                user_id=request.user.id,
            )

            return RegistrationReadDetailedSerializer(reg).data
        except ObjectDoesNotExist:
            return None

    def get_photo_consents(self, obj: Event):
        request: HttpRequest = self.context.get("request", None)
        if not request or not request.user.is_authenticated:
            return []

        # Only return consents for events that use consent
        if not obj.use_consent:
            return []

        # If the user is not allowed to register and is not registered,
        # there is no need for consents
        if (
            not obj.is_admitted(request.user)
            and not obj.is_on_waiting_list(request.user)
            and len(obj.get_possible_pools(request.user, future=True)) == 0
        ):
            return []

        pc = PhotoConsent.get_consents(request.user, time=obj.start_time)
        return PhotoConsentSerializer(instance=pc, many=True).data


class EventReadAuthUserDetailedSerializer(EventReadUserDetailedSerializer):
    pools = PoolReadAuthSerializer(many=True)
    waiting_registrations = RegistrationReadSerializer(many=True)
    unanswered_surveys = serializers.SerializerMethodField()
    created_by = PublicUserSerializer()
    responsible_users = PublicUserField(
        queryset=User.objects.all(),
        allow_null=False,
        required=True,
        many=True,
    )

    class Meta(EventReadUserDetailedSerializer.Meta):
        fields = EventReadUserDetailedSerializer.Meta.fields + (  # type: ignore
            "created_by",
            "responsible_users",
            "waiting_registrations",
            "unanswered_surveys",
        )

    def get_unanswered_surveys(self, obj):
        request = self.context.get("request", None)
        return request.user.unanswered_surveys()


class EventAdministrateSerializer(EventReadSerializer, EventReadDetailedSerializer):
    pools = PoolAdministrateSerializer(many=True)
    unregistered = RegistrationReadDetailedSerializer(many=True)
    waiting_registrations = RegistrationReadDetailedSerializer(many=True)
    responsible_group = AbakusGroupField(
        queryset=AbakusGroup.objects.all(), required=False, allow_null=True
    )
    responsible_users = PublicUserField(
        queryset=User.objects.all(),
        allow_null=False,
        required=True,
        many=True,
    )

    class Meta(EventReadSerializer.Meta):
        fields = EventReadSerializer.Meta.fields + (  # type: ignore
            "pools",
            "responsible_users",
            "unregistered",
            "waiting_registrations",
            "use_consent",
            "created_by",
            "feedback_required",
            "responsible_group",
        )


class EventAdministrateAllergiesSerializer(EventAdministrateSerializer):
    pools = PoolAdministrateAllergiesSerializer(many=True)
    waiting_registrations = RegistrationReadDetailedAllergiesSerializer(many=True)


class EventCreateAndUpdateSerializer(
    TagSerializerMixin, BasisModelSerializer, ObjectPermissionsSerializerMixin
):
    cover = ImageField(required=False, options={"height": 500})
    responsible_group = AbakusGroupField(
        queryset=AbakusGroup.objects.all(), required=False, allow_null=True
    )
    pools = PoolCreateAndUpdateSerializer(many=True, required=False)
    text = ContentSerializerField()

    registration_close_time = serializers.DateTimeField(read_only=True)
    unregistration_close_time = serializers.DateTimeField(read_only=True)
    responsible_users = PublicUserField(
        queryset=User.objects.all(),
        allow_null=False,
        allow_empty=True,
        required=False,
        many=True,
    )

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
            "registration_deadline_hours",
            "registration_close_time",
            "unregistration_close_time",
            "youtube_url",
            "mazemap_poi",
            "responsible_users",
            "is_foreign_language",
            "show_company_description",
        ) + ObjectPermissionsSerializerMixin.Meta.fields

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
        return data

    def create(self, validated_data):
        pools = validated_data.pop("pools", [])
        event_status_type = validated_data.get(
            "event_status_type", Event._meta.get_field("event_status_type").default
        )
        require_auth = validated_data.get("require_auth", False)
        validated_data["require_auth"] = require_auth
        if event_status_type == constants.TBA:
            pools = []
        elif event_status_type == constants.OPEN:
            pools = []
        elif event_status_type == constants.INFINITE:
            pools = [pools[0]]
            pools[0]["capacity"] = 0
        with transaction.atomic():
            event = super().create(validated_data)
            for pool in pools:
                permission_groups = pool.get("permission_groups", [])
                pool_data = {
                    "name": pool.get("name"),
                    "capacity": pool.get("capacity"),
                    "activation_date": pool.get("activation_date"),
                    "permission_groups": [
                        getattr(gr, "id", gr) for gr in permission_groups
                    ],
                }
                pool_serializer = PoolCreateAndUpdateSerializer(
                    data=pool_data, context={**self.context, "event": event}
                )
                pool_serializer.is_valid(raise_exception=True)
                pool_serializer.save()
            return event

    def update(self, instance, validated_data):
        pools = validated_data.pop("pools", None)
        event_status_type = validated_data.get(
            "event_status_type", Event._meta.get_field("event_status_type").default
        )
        if event_status_type == constants.TBA:
            pools = []
        elif event_status_type == constants.OPEN:
            pools = []
        elif event_status_type == constants.INFINITE:
            pools = [pools[0]]
            pools[0]["capacity"] = 0
        with transaction.atomic():
            if pools is not None:
                existing_ids = set(instance.pools.values_list("id", flat=True))
                for pool in pools:
                    pool_id = pool.get("id")
                    pool_instance = (
                        Pool.objects.filter(id=pool_id, event=instance)
                        .select_for_update()
                        .first()
                        if pool_id
                        else None
                    )
                    if pool_instance:
                        existing_ids.discard(pool_id)
                    permission_groups = pool.get("permission_groups", [])
                    pool_data = {
                        "name": pool.get("name"),
                        "capacity": pool.get("capacity"),
                        "activation_date": pool.get("activation_date"),
                        "permission_groups": [
                            getattr(gr, "id", gr) for gr in permission_groups
                        ],
                    }
                    pool_serializer = PoolCreateAndUpdateSerializer(
                        instance=pool_instance,
                        data=pool_data,
                        context={**self.context, "event": instance},
                        partial=True,
                    )
                    pool_serializer.is_valid(raise_exception=True)
                    pool_serializer.save()
                if existing_ids:
                    for pool_obj in Pool.objects.filter(
                        event=instance, id__in=existing_ids
                    ).iterator():
                        pool_obj.delete()
            return super().update(instance, validated_data)


class FrontpageEventSerializer(serializers.ModelSerializer):
    cover = ImageField(required=False, options={"height": 500})
    cover_placeholder = ImageField(
        source="cover", required=False, options={"height": 50, "filters": ["blur(20)"]}
    )
    thumbnail = ImageField(
        source="cover",
        required=False,
        options={"height": 500, "width": 500, "smart": True},
    )
    text = ContentSerializerField()
    activation_time = ActivationTimeField()
    is_admitted = IsAdmittedField()
    registration_count = RegistrationCountField()
    total_capacity = TotalCapacityField()

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "cover",
            "cover_placeholder",
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

    def get_grade(r):
        user = r.get("user", {})
        abakus_groups = user.get("abakus_groups", [])
        user["grade"] = None
        for id in abakus_groups:
            grade = grade_dict.get(id, None)
            if grade:
                user["grade"] = grade

    grades = AbakusGroup.objects.filter(type=GROUP_GRADE).values("id", "name")
    grade_dict = {item["id"]: item for item in grades}

    for pool in event_dict.get("pools", []):
        for registration in pool.get("registrations", []):
            get_grade(registration)

    for reg in event_dict.get("waiting_registrations", []):
        get_grade(reg)

    return event_dict
