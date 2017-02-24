from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework_jwt.serializers import User

from lego.apps.comments.serializers import CommentSerializer
from lego.apps.companies.serializers import PublicCompanyReadSerializer
from lego.apps.events.fields import ActivationTimeField, ChargeStatusField
from lego.apps.events.models import Event, Pool, Registration
from lego.apps.files.fields import ImageField
from lego.apps.tags.serializers import TagSerializerMixin
from lego.apps.users.serializers.abakus_groups import PublicAbakusGroupSerializer
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.fields import PrimaryKeyRelatedFieldNoPKOpt
from lego.utils.serializers import BasisModelSerializer


class RegistrationReadSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    charge_status = ChargeStatusField()

    class Meta:
        model = Registration
        fields = ('id', 'user', 'pool', 'feedback', 'status', 'charge_status')
        read_only = True


class PoolReadSerializer(BasisModelSerializer):
    registrations = RegistrationReadSerializer(many=True)
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
    pools = PoolReadSerializer(read_only=True, many=True)
    active_capacity = serializers.ReadOnlyField()
    price = serializers.SerializerMethodField()
    activation_time = ActivationTimeField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'cover', 'text', 'event_type', 'location',
                  'comments', 'comment_target', 'start_time', 'end_time', 'pools', 'company',
                  'active_capacity', 'feedback_required', 'is_priced', 'price', 'activation_time',
                  'tags')
        read_only = True

    def get_price(self, obj):
        request = self.context.get('request', None)
        if request:
            return obj.get_price(user=request.user)


class PoolCreateAndUpdateSerializer(BasisModelSerializer):

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
    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'text', 'event_type', 'location',
                  'start_time', 'end_time', 'merge_time', 'tags')


class RegistrationCreateAndUpdateSerializer(BasisModelSerializer):
    captcha_response = serializers.CharField(required=False)

    class Meta:
        model = Registration
        fields = ('id', 'feedback', 'captcha_response')


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
