from typing import Any

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpRequest
from django.utils import timezone
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
    WaitingRegistrationCountField,
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
from lego.apps.permissions.constants import CREATE
from lego.apps.permissions.utils import get_permission_handler
from lego.apps.tags.serializers import TagSerializerMixin
from lego.apps.users.constants import GROUP_GRADE, GROUP_INTEREST, MEMBER_GROUP
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
    responsible_group = PublicAbakusGroupSerializer(read_only=True)
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
            "responsible_group",
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
    registration_count = RegistrationCountField()
    waiting_registration_count = WaitingRegistrationCountField()
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
            "registration_count",
            "waiting_registration_count",
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

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """
        The frontend only sends id and capacity for interest event pools, so
        the backend-owned pool fields get placeholders before field
        validation. force_interest_event_pools replaces them in validate.
        """
        if isinstance(data, dict):
            event_type = data.get(
                "event_type", self.instance.event_type if self.instance else None
            )
            if event_type == constants.INTEREST_EVENT and data.get("pools"):
                member_group_id = AbakusGroup.objects.get(name=MEMBER_GROUP).pk
                for pool in data["pools"]:
                    if isinstance(pool, dict):
                        pool.setdefault("name", MEMBER_GROUP)
                        pool.setdefault("activation_date", timezone.now())
                        pool.setdefault("permission_groups", [member_group_id])
        return super().to_internal_value(data)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
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

        instance = self.instance if isinstance(self.instance, Event) else None
        event_type = data.get("event_type", instance.event_type if instance else None)
        if event_type == constants.INTEREST_EVENT:
            self.enforce_interest_event_contract(data, instance)
        return data

    def enforce_interest_event_contract(
        self, data: dict[str, Any], instance: Event | None
    ) -> None:
        """
        Interest events are open to every Abakus member from creation until
        start, always free, and never pinned. Creators only control the
        whitelisted content fields - see the contract in constants.py.
        """
        responsible_group = data.get(
            "responsible_group",
            instance.responsible_group if instance else None,
        )
        if not responsible_group or responsible_group.type != GROUP_INTEREST:
            raise serializers.ValidationError(
                {
                    "responsible_group": "Interest events must be organized "
                    "by an interest group"
                }
            )
        self.validate_interest_event_group_change(data, instance)
        for field in (
            set(data)
            - constants.INTEREST_EVENT_CREATOR_FIELDS
            - set(constants.INTEREST_EVENT_FORCED_FIELDS)
        ):
            data.pop(field)
        data.update(constants.INTEREST_EVENT_FORCED_FIELDS)
        if instance is None or "pools" in data:
            data["pools"] = self.force_interest_event_pools(data.get("pools"))

    def validate_interest_event_group_change(
        self, data: dict[str, Any], instance: Event | None
    ) -> None:
        """
        The permission layer only checks leadership of the responsible group
        in request data, so a PATCH without event_type could move an event to
        a group the requester does not lead.
        """
        if (
            instance is None
            or "responsible_group" not in data
            or data["responsible_group"] == instance.responsible_group
        ):
            return
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return
        handler = get_permission_handler(Event)
        allowed = request.user.has_perm(
            handler.event_type_keyword_permissions(constants.INTEREST_EVENT, CREATE)
        ) or handler.is_interest_group_leader(
            request.user, data["responsible_group"].pk
        )
        if not allowed:
            raise serializers.ValidationError(
                {
                    "responsible_group": "You must be a leader of the "
                    "responsible interest group"
                }
            )

    @staticmethod
    def force_interest_event_pools(
        pools: list[dict[str, Any]] | None,
    ) -> list[dict[str, Any]]:
        """
        The single pool on interest events is decided by the backend, not the
        creator: open to every Abakus member immediately, with the creator's
        capacity kept. A non-empty pool keeps its stored values, as edits to
        it are rejected by PoolCreateAndUpdateSerializer.
        """
        pool = (pools or [{}])[0]
        pool.setdefault("name", MEMBER_GROUP)
        existing = (
            Pool.objects.filter(id=pool["id"]).first() if pool.get("id") else None
        )
        if existing and existing.registration_count > 0:
            pool["activation_date"] = existing.activation_date
            pool["permission_groups"] = list(existing.permission_groups.all())
        else:
            pool["activation_date"] = timezone.now()
            pool["permission_groups"] = [AbakusGroup.objects.get(name=MEMBER_GROUP)]
        return [pool]

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
            pools[0].setdefault("capacity", 0)
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
            "event_status_type", instance.event_status_type
        )
        if event_status_type == constants.TBA:
            pools = []
        elif event_status_type == constants.OPEN:
            pools = []
        elif event_status_type == constants.INFINITE and pools:
            pools = [pools[0]]
            pools[0].setdefault("capacity", 0)
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
