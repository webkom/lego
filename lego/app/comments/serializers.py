from basis.serializers import BasisSerializer
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, DateTimeField

from lego.app.comments.models import Comment
from lego.users.serializers import PublicUserSerializer


class CommentSerializer(BasisSerializer):
    author = PublicUserSerializer(read_only=True, source='created_by')
    comment_target = CharField(write_only=True)
    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'comment_target', 'created_at', 'updated_at', 'parent')

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance

    def create(self, validated_data):
        try:
            content_type, object_id = validated_data.pop('comment_target').split('-')
        except ValueError:
            raise ValidationError({
                'comment_target': 'Source should be in the form "[ContentType]-[ObjectId]"'
            })

        try:
            validated_data['content_type'] = ContentType.objects.get(app_label=content_type)
        except ContentType.DoesNotExist:
            raise ValidationError({
                'comment_target': 'content_type does not exist'
            })

        model_class = validated_data['content_type'].model_class()
        try:
            parent_instance = model_class.objects.get(pk=object_id)
        except model_class.DoesNotExist:
            raise ValidationError({
                'comment_target': 'object_id {0} does not exist in database'.format(object_id)
            })

        if not parent_instance.can_view(self.context['request'].user):
            raise PermissionDenied('You do not have permission to view the comment_target')

        validated_data['object_id'] = int(object_id)

        if 'parent' in validated_data:
            parent = validated_data['parent']
            if (parent.object_id != validated_data['object_id'] or
                    parent.content_type.id != validated_data['content_type'].id):
                raise ValidationError({
                    'parent': 'parent does not point to the same comment_target'
                })

        return Comment.objects.create(**validated_data)
