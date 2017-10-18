from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import CharField

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.fields import CompanyField
from lego.apps.companies.models import Company
from lego.apps.events.fields import ActivationTimeField, SpotsLeftField
from lego.apps.events.models import Event, Pool
from lego.apps.events.serializers.pools import (PoolAdministrateSerializer,
                                                PoolCreateAndUpdateSerializer, PoolReadSerializer)
from lego.apps.events.serializers.registrations import (RegistrationReadDetailedSerializer,
                                                        RegistrationReadSerializer)
from lego.apps.files.fields import ImageField
from lego.apps.tags.serializers import TagSerializerMixin
from lego.utils.serializers import BasisModelSerializer


class EventPublicSerializer(BasisModelSerializer):
    thumbnail = ImageField(
        source='cover',
        required=False,
        options={'height': 500, 'width': 500, 'smart': True}
    )

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'event_type',
                  'location', 'thumbnail')
        read_only = True


class EventReadSerializer(TagSerializerMixin, BasisModelSerializer):
    company = CompanyField(queryset=Company.objects.all())
    cover = ImageField(required=False, options={'height': 500})
    thumbnail = ImageField(
        source='cover',
        required=False,
        options={'height': 500, 'width': 500, 'smart': True}
    )

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'cover', 'event_type',
                  'location', 'start_time', 'thumbnail',
                  'total_capacity', 'company', 'registration_count', 'tags')
        read_only = True


class EventReadDetailedSerializer(TagSerializerMixin, BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    cover = ImageField(required=False, options={'height': 500})
    company = CompanyField(queryset=Company.objects.all())
    pools = PoolReadSerializer(many=True)
    active_capacity = serializers.ReadOnlyField()
    price = serializers.SerializerMethodField()
    waiting_registrations = RegistrationReadSerializer(many=True)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'cover', 'text', 'event_type', 'location',
                  'comments', 'comment_target', 'start_time', 'end_time', 'merge_time',
                  'pools', 'company', 'active_capacity', 'feedback_description',
                  'feedback_required', 'is_priced', 'price', 'price_member', 'price_guest',
                  'use_stripe', 'use_captcha', 'waiting_registrations', 'tags', 'is_merged')
        read_only = True

    def get_price(self, obj):
        request = self.context.get('request', None)
        if request:
            return obj.get_price(user=request.user)


class EventReadUserDetailedSerializer(EventReadDetailedSerializer):
    """ User specfic event serializer that appends data based on request.user """
    activation_time = ActivationTimeField()
    spots_left = SpotsLeftField()

    class Meta(EventReadDetailedSerializer.Meta):
        fields = EventReadDetailedSerializer.Meta.fields + ('activation_time', 'spots_left')


class EventAdministrateSerializer(EventReadSerializer):
    pools = PoolAdministrateSerializer(many=True)
    unregistered = RegistrationReadDetailedSerializer(many=True)
    waiting_registrations = RegistrationReadDetailedSerializer(many=True)

    class Meta(EventReadSerializer.Meta):
        fields = EventReadSerializer.Meta.fields + ('pools', 'unregistered',
                                                    'waiting_registrations')


class EventCreateAndUpdateSerializer(TagSerializerMixin, BasisModelSerializer):
    cover = ImageField(required=False, options={'height': 500})
    pools = PoolCreateAndUpdateSerializer(many=True, required=False)

    class Meta:
        model = Event
        fields = ('id', 'title', 'cover', 'description', 'text', 'company', 'feedback_description',
                  'feedback_required', 'event_type', 'location', 'is_priced', 'price_member',
                  'price_guest', 'use_stripe', 'start_time', 'end_time', 'merge_time',
                  'use_captcha', 'tags', 'pools', 'is_ready')
        extra_kwargs = {'is_ready': {'required': False}}

    def create(self, validated_data):
        pools = validated_data.pop('pools', [])
        with transaction.atomic():
            event = super().create(validated_data)
            for pool in pools:
                permission_groups = pool.pop('permission_groups')
                created_pool = Pool.objects.create(event=event, **pool)
                created_pool.permission_groups.set(permission_groups)

            return event

    def update(self, instance, validated_data):
        pools = validated_data.pop('pools', None)
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
                            'unregistration_deadline': pool.get('unregistration_deadline', None)
                        }
                    )[0]
                    created_pool.permission_groups.set(permission_groups)
                for pool_id in existing_pools:
                    Pool.objects.get(id=pool_id).delete()

            return super().update(instance, validated_data)


class EventSearchSerializer(serializers.ModelSerializer):
    cover = ImageField(required=False, options={'height': 500})
    thumbnail = ImageField(
        source='cover',
        required=False,
        options={'height': 500, 'width': 500, 'smart': True}
    )

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'cover', 'text', 'event_type',
                  'location', 'start_time', 'thumbnail', 'end_time',
                  'total_capacity', 'company', 'registration_count', 'tags')
        read_only = True
