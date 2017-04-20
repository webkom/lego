from lego.apps.companies.serializers import (CompanyContactReadSerializer,
                                             PublicCompanyReadSerializer)
from lego.apps.joblistings.models import Joblisting, Workplace
from lego.utils.serializers import BasisModelSerializer
from rest_framework.utils import model_meta
from rest_framework.compat import set_many


class WorkplaceSerializer(BasisModelSerializer):
    class Meta:
        model = Workplace
        fields = ('id', 'town')


class JoblistingSerializer(BasisModelSerializer):
    workplaces = WorkplaceSerializer(many=True)
    company = PublicCompanyReadSerializer()

    class Meta:
        model = Joblisting
        fields = ('id', 'title', 'company', 'deadline', 'job_type', 'workplaces',
                  'from_year', 'to_year')


class JoblistingDetailedSerializer(BasisModelSerializer):
    workplaces = WorkplaceSerializer(many=True)
    company = PublicCompanyReadSerializer()
    responsible = CompanyContactReadSerializer()

    class Meta:
        model = Joblisting
        fields = ('id', 'title', 'text', 'company', 'responsible', 'description', 'deadline',
                  'job_type', 'workplaces', 'visible_from', 'visible_to', 'from_year', 'to_year',
                  'application_url')


class JoblistingCreateAndUpdateSerializer(BasisModelSerializer):
    workplaces = WorkplaceSerializer(many=True)

    class Meta:
        model = Joblisting
        fields = ('id', 'title', 'text', 'company', 'responsible', 'description', 'deadline',
                  'visible_from', 'visible_to', 'job_type', 'workplaces', 'from_year',
                  'to_year', 'application_url')

    def create(self, validated_data):
        workplaces_data = validated_data.pop('workplaces')
        joblisting = Joblisting.objects.create(**validated_data)

        for workplace_item in workplaces_data:
            workplace, created = Workplace.objects.get_or_create(town=workplace_item['town'])
            joblisting.workplaces.add(workplace)
        return joblisting

    def update(self, instance, validated_data):
        workplaces_data = validated_data.pop('workplaces')
        info = model_meta.get_field_info(instance)
        new_workplaces = []

        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                set_many(instance, attr, value)
            else:
                setattr(instance, attr, value)

        for workplace_item in workplaces_data:
            workplace, created = Workplace.objects.get_or_create(town=workplace_item['town'])
            new_workplaces.append(workplace)
        setattr(instance, 'workplaces', new_workplaces)

        instance.save()

        return instance
