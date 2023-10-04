from rest_framework import serializers


from lego.apps.lending.models import LendableObject, LendingInstance


class LendableObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = LendableObject
        fields = "__all__"


class LendingInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LendingInstance
        fields = "__all__"

    def validate(self, data):
        lendable_object_id = data["lendable_object"].id
        lendable_object = LendableObject.objects.get(id=lendable_object_id)
        user = self.request.user

        if not user.abakus_groups.filter(
            id__in=lendable_object.responsible_groups.all().values_list("id", flat=True)
        ).exists():
            if (
                data["end_date"] - data["start_date"]
                > lendable_object.max_lending_period
            ):
                raise serializers.ValidationError(
                    "Lending period exceeds maximum allowed duration"
                )

            # Add additional validation logic as per your use case
            # ...

        return data
