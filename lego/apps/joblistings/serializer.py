from lego.apps.joblistings.models import Joblisting
from lego.utils.serializers import BasisModelSerializer


class JoblistingSerializer(BasisModelSerializer):
    class Meta:
        model = Joblisting
        fields = ('title', 'deadline', 'job_type', 'workplaces',
                  'from_year', 'to_year')


class JoblistingDetailedSerializer(BasisModelSerializer):
    class Meta:
        model = Joblisting
        fields = ('title', 'content', 'deadline', 'visible_from', 'visible_to',
                  'job_type', 'workplaces', 'from_year', 'to_year',
                  'application_url', 'application_email')


class JoblistingCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = Joblisting
        fields = ('title', 'content', 'deadline', 'visible_from', 'visible_to',
                  'job_type', 'workplaces', 'from_year', 'to_year',
                  'application_url', 'application_email')
