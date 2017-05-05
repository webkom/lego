from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework_jwt.serializers import User

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.serializers import PublicCompanyReadSerializer
from lego.apps.events import constants
from lego.apps.events.fields import (ActivationTimeField, ChargeStatusField, FeedbackField,
                                     PresenceField, SetChargeStatusField, SpotsLeftField)
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.files.fields import ImageField
from lego.apps.tags.serializers import TagSerializerMixin
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.users import AdministrateUserSerializer, PublicUserSerializer
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer


class RegistrationReadSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    feedback = FeedbackField()

    class Meta:
        model = Registration
        fields = ('id', 'user', 'pool', 'feedback', 'status')
        read_only = True


class RegistrationPaymentReadSerializer(RegistrationReadSerializer):
    charge_status = ChargeStatusField()

    class Meta(RegistrationReadSerializer.Meta):
        fields = RegistrationReadSerializer.Meta.fields + ('charge_status', )


class RegistrationReadDetailedSerializer(BasisModelSerializer):
    user = AdministrateUserSerializer()

    class Meta:
        model = Registration
        fields = ('id', 'user', 'pool', 'event', 'presence', 'feedback', 'status',
                  'registration_date', 'unregistration_date', 'admin_reason',
                  'charge_id', 'charge_status', 'charge_amount', 'charge_amount_refunded')
        read_only = True


class PoolReadSerializer(BasisModelSerializer):
    registrations = serializers.SerializerMethodField()
    permission_groups = PublicAbakusGroupSerializer(many=True)

    class Meta:
        model = Pool
        fields = ('id', 'name', 'capacity', 'activation_date',
                  'permission_groups', 'registrations')
        read_only = True

    def create(self, validated_data):
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        permission_groups = validated_data.pop('permission_groups')
        pool = Pool.objects.create(event=event, **validated_data)
        pool.permission_groups.set(permission_groups)

        return pool

    def get_registrations(self, obj):
        queryset = obj.registrations.all()
        if obj.event.is_priced:
            return RegistrationPaymentReadSerializer(
                queryset, context=self.context, many=True
            ).data
        return RegistrationReadSerializer(queryset, context=self.context, many=True).data


class PoolAdministrateSerializer(PoolReadSerializer):
    registrations = RegistrationReadDetailedSerializer(many=True)


class EventReadSerializer(TagSerializerMixin, BasisModelSerializer):
    company = PublicCompanyReadSerializer(read_only=True)
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


class EventReadDetailedSerializer(TagSerializerMixin, BasisModelSerializer):
    comments = CommentSerializer(read_only=True, many=True)
    comment_target = CharField(read_only=True)
    cover = ImageField(required=False, options={'height': 500})
    company = PublicCompanyReadSerializer(read_only=True)
    pools = PoolReadSerializer(many=True)
    active_capacity = serializers.ReadOnlyField()
    price = serializers.SerializerMethodField()
    waiting_registrations = RegistrationReadSerializer(many=True)
    activation_time = ActivationTimeField()
    spots_left = SpotsLeftField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'cover', 'text', 'event_type', 'location',
                  'comments', 'comment_target', 'start_time', 'end_time', 'pools', 'company',
                  'active_capacity', 'feedback_required', 'is_priced', 'price', 'use_stripe',
                  'use_captcha', 'waiting_registrations', 'activation_time', 'spots_left', 'tags')
        read_only = True

    def get_price(self, obj):
        request = self.context.get('request', None)
        if request:
            return obj.get_price(user=request.user)


class EventAdministrateSerializer(EventReadSerializer):
    pools = PoolAdministrateSerializer(many=True)
    unregistered = RegistrationReadDetailedSerializer(many=True)
    waiting_registrations = RegistrationReadDetailedSerializer(many=True)

    class Meta(EventReadSerializer.Meta):
        fields = EventReadSerializer.Meta.fields + ('pools', 'unregistered',
                                                    'waiting_registrations')


class PoolCreateAndUpdateSerializer(BasisModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Pool
        fields = ('id', 'name', 'capacity', 'activation_date', 'permission_groups')

    def create(self, validated_data):
        event = Event.objects.get(pk=self.context['view'].kwargs['event_pk'])
        permission_groups = validated_data.pop('permission_groups')
        pool = Pool.objects.create(event=event, **validated_data)
        pool.permission_groups.set(permission_groups)

        return pool


class EventCreateAndUpdateSerializer(TagSerializerMixin, BasisModelSerializer):
    pools = PoolCreateAndUpdateSerializer(many=True)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'text', 'company', 'event_type',
                  'location', 'is_priced', 'price_member', 'use_stripe', 'start_time',
                  'end_time', 'merge_time', 'use_captcha', 'tags', 'pools')

    def create(self, validated_data):
        pools = validated_data.pop('pools')
        event = super().create(validated_data)
        for pool in pools:
            permission_groups = pool.pop('permission_groups')
            created_pool = Pool.objects.create(event=event, **pool)
            created_pool.permission_groups.set(permission_groups)

        return event

    def update(self, instance, validated_data):
        pools = validated_data.pop('pools')
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            existing_pools = list(instance.pools.all().values_list('id', flat=True))
            for pool in pools:
                id = pool.get('id', None)
                if id in existing_pools:
                    existing_pools.remove(id)
                permission_groups = pool.pop('permission_groups')
                created_pool = Pool.objects.update_or_create(event=instance, id=id, defaults={
                    'name': pool.get('name'),
                    'capacity': pool.get('capacity', 0),
                    'activation_date': pool.get('activation_date'),
                    'unregistration_deadline': pool.get('unregistration_deadline', None)
                })[0]
                created_pool.permission_groups.set(permission_groups)
            for id in existing_pools:
                Pool.objects.get(id=id).delete()

        return instance


class RegistrationCreateAndUpdateSerializer(BasisModelSerializer):
    captcha_response = serializers.CharField(required=False)
    charge_status = SetChargeStatusField(
        required=False, choices=(constants.PAYMENT_MANUAL, constants.PAYMENT_FAILURE)
    )
    presence = PresenceField(required=False, choices=constants.PRESENCE_CHOICES)

    class Meta:
        model = Registration
        fields = ('id', 'feedback', 'presence', 'captcha_response', 'charge_status')


class StripeTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class StripeObjectSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount = serializers.IntegerField()
    amount_refunded = serializers.IntegerField()
    status = serializers.CharField()


class AdminRegistrationCreateAndUpdateSerializer(serializers.Serializer):
    user = PrimaryKeyRelatedFieldNoPKOpt(queryset=User.objects.all())
    pool = PrimaryKeyRelatedFieldNoPKOpt(queryset=Pool.objects.all())
    feedback = serializers.CharField(required=False)
    admin_reason = serializers.CharField(required=True)


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
