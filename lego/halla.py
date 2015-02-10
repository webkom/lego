from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        request = self.context['request']
        article = self.Meta.model.objects.create(created_by=request.user, **validated_data)
        return article

    def update(self, instance, validated_data):
        request = self.context['request']
        instance.updated_by = request.user
        return instance
