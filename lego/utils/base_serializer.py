from rest_framework import serializers


class BasisSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        request = self.context['request']
        kwargs['current_user'] = request.user
        super(BasisSerializer, self).save(**kwargs)
