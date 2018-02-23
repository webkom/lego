from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import BooleanField, CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.fields import CompanyField
from lego.apps.companies.models import Company
from lego.apps.content.fields import ContentSerializerField
from lego.apps.events.fields import ActivationTimeField, SpotsLeftField
from lego.apps.events.models import Event, Pool
from lego.apps.events.serializers.pools import (
    PoolAdministrateSerializer, PoolCreateAndUpdateSerializer, PoolReadAuthSerializer,
    PoolReadSerializer
)
from lego.apps.events.serializers.registrations import (
    RegistrationReadDetailedSerializer, RegistrationReadSerializer
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
        source='cover', required=False, options={
            'height': 500,
            'width': 500,
            'smart': True
        }
    )

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'event_type', 'location', 'thumbnail')
        read_only = True


class EventReadSerializer(TagSerializerMixin, BasisModelSerializer):
    company = CompanyField(queryset=Company.objects.all())
    cover = ImageField(required=False, options={'height': 500})
    thumbnail = ImageField(
        source='cover', required=False, options={
            'height': 500,
            'width': 500,
            'smart': True
        }
    )

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'cover', 'event_type', 'location', 'start_time',
            'thumbnail', 'total_capacity', 'company', 'registration_count', 'tags'
        )
        read_only = True


class EventReadDetailedSerializer(TagSerializerMixin, BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    cover = ImageField(required=False, options={'height': 500})
    company = CompanyField(queryset=Company.objects.all())
    responsible_group = AbakusGroupField(
        queryset=AbakusGroup.objects.all(), required=False, allow_null=True
    )
    pools = PoolReadSerializer(many=True)
    active_capacity = serializers.ReadOnlyField()
    text = ContentSerializerField()
    created_by = PublicUserSerializer()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'cover', 'text', 'event_type', 'location', 'comments',
            'comment_target', 'start_time', 'end_time', 'merge_time', 'pools',
            'unregistration_deadline', 'company', 'responsible_group', 'active_capacity',
            'feedback_description', 'feedback_required', 'is_priced', 'price_member', 'price_guest',
            'use_stripe', 'payment_due_date', 'use_captcha', 'waiting_registration_count', 'tags',
            'is_merged', 'heed_penalties', 'created_by', 'is_abakom_only'
        )
        read_only = True


class EventReadUserDetailedSerializer(EventReadDetailedSerializer):
    """ User specfic event serializer that appends data based on request.user """
    activation_time = ActivationTimeField()
    spots_left = SpotsLeftField()
    price = serializers.SerializerMethodField()

    class Meta(EventReadDetailedSerializer.Meta):
        fields = EventReadDetailedSerializer.Meta.fields + \
                 ('price', 'activation_time', 'spots_left')

    def get_price(self, obj):
        request = self.context.get('request', None)
        if request:
            return obj.get_price(user=request.user)


class EventReadAuthUserDetailedSerializer(EventReadUserDetailedSerializer):
    pools = PoolReadAuthSerializer(many=True)
    waiting_registrations = RegistrationReadSerializer(many=True)

    class Meta(EventReadUserDetailedSerializer.Meta):
        fields = EventReadUserDetailedSerializer.Meta.fields + ('waiting_registrations', )


class EventAdministrateSerializer(EventReadSerializer):
    pools = PoolAdministrateSerializer(many=True)
    unregistered = RegistrationReadDetailedSerializer(many=True)
    waiting_registrations = RegistrationReadDetailedSerializer(many=True)

    class Meta(EventReadSerializer.Meta):
        fields = EventReadSerializer.Meta.fields + (
            'pools', 'unregistered', 'waiting_registrations'
        )


class EventCreateAndUpdateSerializer(TagSerializerMixin, BasisModelSerializer):
    cover = ImageField(required=False, options={'height': 500})
    responsible_group = AbakusGroupField(
        queryset=AbakusGroup.objects.all(), required=False, allow_null=True
    )
    pools = PoolCreateAndUpdateSerializer(many=True, required=False)
    text = ContentSerializerField()
    is_abakom_only = BooleanField(required=False, default=False)

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'cover', 'description', 'text', 'company', 'responsible_group',
            'feedback_description', 'feedback_required', 'event_type', 'location', 'is_priced',
            'price_member', 'price_guest', 'use_stripe', 'payment_due_date', 'start_time',
            'end_time', 'merge_time', 'use_captcha', 'tags', 'pools', 'unregistration_deadline',
            'pinned', 'heed_penalties', 'is_abakom_only'
        )

    def create(self, validated_data):
        pools = validated_data.pop('pools', [])
        is_abakom_only = validated_data.pop('is_abakom_only', False)
        with transaction.atomic():
            event = super().create(validated_data)
            for pool in pools:
                permission_groups = pool.pop('permission_groups')
                created_pool = Pool.objects.create(event=event, **pool)
                created_pool.permission_groups.set(permission_groups)
            event.set_abakom_only(is_abakom_only)
            return event

    def update(self, instance, validated_data):
        pools = validated_data.pop('pools', None)
        is_abakom_only = validated_data.pop('is_abakom_only', False)
        with transaction.atomic():
            if pools is not None:
                existing_pools = list(instance.pools.all().values_list('id', flat=True))
                for pool in pools:
                    pool_id = pool.get('id', None)
                    if pool_id in existing_pools:
                        existing_pools.remove(pool_id)
                    permission_groups = pool.pop('permission_groups')
                    created_pool = Pool.objects.update_or_create(
                        event=instance, id=pool_id, defaults={
                            'name': pool.get('name'),
                            'capacity': pool.get('capacity', 0),
                            'activation_date': pool.get('activation_date'),
                        }
                    )[0]
                    created_pool.permission_groups.set(permission_groups)
                for pool_id in existing_pools:
                    Pool.objects.get(id=pool_id).delete()
            instance.set_abakom_only(is_abakom_only)
            return super().update(instance, validated_data)


class EventSearchSerializer(serializers.ModelSerializer):
    cover = ImageField(required=False, options={'height': 500})
    thumbnail = ImageField(
        source='cover', required=False, options={
            'height': 500,
            'width': 500,
            'smart': True
        }
    )
    text = ContentSerializerField()

    class Meta:
        model = Event
        fields = (
            'id', 'title', 'description', 'cover', 'text', 'event_type', 'location', 'start_time',
            'thumbnail', 'end_time', 'total_capacity', 'company', 'registration_count', 'tags',
            'pinned'
        )
        read_only = True


def populate_event_registration_users_with_grade(event_dict):
    """
    Populates every user in registrations in a serialized event with `grade`.
    Mainly used in the administrate endpoint
    :param event_dict:
    :return:
    """
    grades = AbakusGroup.objects.filter(type=GROUP_GRADE).values('id', 'name')
    grade_dict = {item['id']: item for item in grades}
    for pool in event_dict.get('pools', []):
        for registration in pool.get('registrations', []):
            user = registration.get('user', {})
            abakus_groups = user.get('abakus_groups', [])
            user['grade'] = None
            for id in abakus_groups:
                grade = grade_dict.get(id, None)
                if grade:
                    user['grade'] = grade
    return event_dict
