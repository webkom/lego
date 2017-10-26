from lego.apps.companies.fields import CompanyContactField, CompanyField
from lego.apps.companies.models import Company, CompanyContact
from lego.apps.content.fields import ContentSerializerField
from lego.apps.joblistings.models import Joblisting, Workplace
from lego.utils.serializers import BasisModelSerializer


class WorkplaceSerializer(BasisModelSerializer):
    class Meta:
        model = Workplace
        fields = ('id', 'town')


class JoblistingSerializer(BasisModelSerializer):
    workplaces = WorkplaceSerializer(many=True)
    company = CompanyField(queryset=Company.objects.all())

    class Meta:
        model = Joblisting
        fields = ('id', 'title', 'company', 'deadline', 'job_type', 'workplaces',
                  'from_year', 'to_year')


class JoblistingDetailedSerializer(BasisModelSerializer):
    workplaces = WorkplaceSerializer(many=True)
    company = CompanyField(queryset=Company.objects.all())
    responsible = CompanyContactField(queryset=CompanyContact.objects.all())
    text = ContentSerializerField()

    class Meta:
        model = Joblisting
        fields = ('id', 'title', 'text', 'company', 'responsible', 'description', 'deadline',
                  'job_type', 'workplaces', 'visible_from', 'visible_to', 'from_year', 'to_year',
                  'application_url')


class JoblistingCreateAndUpdateSerializer(BasisModelSerializer):
    workplaces = WorkplaceSerializer(many=True)
    text = ContentSerializerField()

    class Meta:
        model = Joblisting
        fields = ('id', 'title', 'text', 'company', 'responsible', 'description', 'deadline',
                  'visible_from', 'visible_to', 'job_type', 'workplaces', 'from_year',
                  'to_year', 'application_url')

    def create(self, validated_data):
        workplaces_data = validated_data.pop('workplaces')
        instance = super().create(validated_data)

        for workplace_item in workplaces_data:
            workplace, created = Workplace.objects.get_or_create(town=workplace_item['town'])
            instance.workplaces.add(workplace)
        return instance

    def update(self, instance, validated_data):
        workplaces_data = validated_data.pop('workplaces')
        instance = super().update(instance, validated_data)
        new_workplaces = []

        for workplace_item in workplaces_data:
            workplace, created = Workplace.objects.get_or_create(town=workplace_item['town'])
            new_workplaces.append(workplace)
        instance.workplaces.set(new_workplaces)

        instance.save()

        return instance
