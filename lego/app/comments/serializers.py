from basis.serializers import BasisSerializer
from django.contrib.contenttypes.models import ContentType

from lego.app.comments.models import Comment
from lego.users.serializers import PublicUserSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField


class CommentSerializer(BasisSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')
    source = CharField()

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'source', 'created_at', 'updated_at')


    def create(self, validated_data):
        try:
            content_type, object_id = validated_data['source'].split('-')
        except ValueError:
            raise ValidationError({
                'source': 'Source should be in the form "[ContentType]-[ObjectId]"'
            })
        validated_data.pop('source')

        try:
            validated_data['content_type'] = ContentType.objects.get(app_label= content_type)
        except ContentType.DoesNotExist:
            raise ValidationError({
                'source': 'content_type does not exist'
            })

        model = validated_data['content_type'].model_class()
        if not model.objects.filter(pk=object_id).exists():
            raise ValidationError({
                'source': 'object_id {0} does not exist in database'.format(object_id)
            })

        validated_data['object_id'] = object_id
        return Comment.objects.create(**validated_data)

