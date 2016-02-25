from basis.serializers import BasisSerializer
from django.contrib.contenttypes.models import ContentType

from lego.app.comments.models import Comment
from lego.users.serializers import PublicUserSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, DateTimeField


class CommentSerializer(BasisSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')
    comment_target = CharField(write_only=True)
    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'comment_target', 'created_at', 'updated_at')

    def validate(self, data):
        instance = self.instance

        if instance is not None:
            if data.get('comment_target') is not None and data.get('comment_target') != instance.get('comment_target'):
                raise ValidationError('Cannot update comment_target')
        return data;

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance

    def create(self, validated_data):
        try:
            content_type, object_id = validated_data['comment_target'].split('-')
        except ValueError:
            raise ValidationError({
                'comment_target': 'Source should be in the form "[ContentType]-[ObjectId]"'
            })
        validated_data.pop('comment_target')

        try:
            validated_data['content_type'] = ContentType.objects.get(app_label= content_type)
        except ContentType.DoesNotExist:
            raise ValidationError({
                'comment_target': 'content_type does not exist'
            })

        model = validated_data['content_type'].model_class()
        if not model.objects.filter(pk=object_id).exists():
            raise ValidationError({
                'comment_target': 'object_id {0} does not exist in database'.format(object_id)
            })

        validated_data['object_id'] = object_id
        return Comment.objects.create(**validated_data)

