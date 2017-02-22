from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from lego.apps.users.models import User


class Trophy(models.Model):
    title = models.TextField()
    description = models.TextField()
    points = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_count = models.PositiveIntegerField()

    def __str__(self):
        return '{0} - {1}'.format(self.title, self.points)


class UserTrophy(models.Model):
    user = models.ForeignKey(User)
    trophy = models.ForeignKey(Trophy)
    award_date = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        unique_together = ('user', 'trophy')

    def get_trophies_for_user(self, user):
        return self.objects.filter(user=user).all()

    def get_trophy_point_count(self, user):
        return self.get_trophies_for_user(user=user)\
            .aggregate(models.Sum('trophy__points'))['trophy__points__sum']
