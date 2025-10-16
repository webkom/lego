from rest_framework import serializers

from lego.apps.events.fields import RegistrationCountField
from lego.apps.events.models import Event, Pool
from lego.apps.events.serializers.registrations import (
    RegistrationPaymentReadSerializer,
    RegistrationReadDetailedAllergiesSerializer,
    RegistrationReadDetailedExportSerializer,
    RegistrationReadDetailedSerializer,
    RegistrationReadSerializer,
)
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.utils.serializers import BasisModelSerializer


class PoolReadSerializer(BasisModelSerializer):
    permission_groups = PublicAbakusGroupSerializer(many=True)
    registration_count = RegistrationCountField()

    class Meta:
        model = Pool
        fields = (
            "id",
            "name",
            "capacity",
            "activation_date",
            "permission_groups",
            "registration_count",
        )
        read_only = True

    def create(self, validated_data):
        event = Event.objects.get(pk=self.context["view"].kwargs["event_pk"])
        permission_groups = validated_data.pop("permission_groups")
        pool = Pool.objects.create(event=event, **validated_data)
        pool.permission_groups.set(permission_groups)

        return pool


class PoolReadAuthSerializer(PoolReadSerializer):
    registrations = serializers.SerializerMethodField()
    all_permission_group_ids = serializers.SerializerMethodField()

    class Meta(PoolReadSerializer.Meta):
        fields = PoolReadSerializer.Meta.fields + (  # type: ignore
            "registrations",
            "all_permission_group_ids",
        )

    def get_registrations(self, obj: Pool):
        queryset = obj.registrations.all()
        if obj.event.is_priced:
            return RegistrationPaymentReadSerializer(
                queryset, context=self.context, many=True
            ).data
        return RegistrationReadSerializer(
            queryset, context=self.context, many=True
        ).data

    def get_all_permission_group_ids(self, obj: Pool):
        return [group.id for group in obj.all_permission_groups]


class PoolAdministrateSerializer(PoolReadAuthSerializer):
    registrations = RegistrationReadDetailedSerializer(many=True)  # type: ignore


class PoolAdministrateExportSerializer(PoolAdministrateSerializer):
    registrations = RegistrationReadDetailedExportSerializer(many=True)  # type: ignore


class PoolAdministrateAllergiesSerializer(PoolAdministrateSerializer):
    registrations = RegistrationReadDetailedAllergiesSerializer(many=True)  # type: ignore


class PoolCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = Pool
        fields = (
            "id",
            "name",
            "capacity",
            "activation_date",
            "registrations",
            "permission_groups",
        )
        extra_kwargs = {
            "id": {"read_only": False, "required": False},
            "registrations": {"read_only": True},
        }

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        if not instance:
            return attrs
        if "permission_groups" in attrs and instance.is_activated:
            new_ids = {getattr(g, "id", g) for g in attrs["permission_groups"]}
            old_ids = instance.permission_group_ids()
            if new_ids != old_ids:
                raise serializers.ValidationError(
                    {
                        "permission_groups": "Permission control is disabled for active pools."
                    }
                )
        if "activation_date" in attrs and instance.is_activated:
            if attrs["activation_date"] != instance.activation_date:
                raise serializers.ValidationError(
                    {"activation_date": "Time travel is disabled for active pools."}
                )
        return attrs

    def create(self, validated_data):
        event = validated_data.pop("event", None) or self.context.get("event")
        if event is None:
            raise serializers.ValidationError({"event": "Event context missing."})
        permission_groups = validated_data.pop("permission_groups")
        pool = Pool.objects.create(event=event, **validated_data)
        pool.permission_groups.set(permission_groups)
        return pool
