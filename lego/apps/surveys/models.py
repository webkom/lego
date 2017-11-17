from django.db import models
from django.utils import timezone

from lego.apps.events.constants import EVENT_TYPES
from lego.apps.surveys.constants import QUESTION_TYPES
from lego.apps.surveys.permissions import SurveyPermissionHandler
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class Survey(BasisModel):
    title = models.CharField(max_length=100)
    active_from = models.DateTimeField(default=timezone.now)
    template_type = models.CharField(max_length=30, choices=EVENT_TYPES, null=True, blank=True)
    event = models.OneToOneField('events.Event')

    @property
    def is_template(self):
        return self.template_type is not None

    class Meta:
        permission_handler = SurveyPermissionHandler()


class Question(BasisModel):

    class Meta:
        ordering = ['relative_index']
        unique_together = ('survey', 'relative_index')

    survey = models.ForeignKey(Survey, related_name='questions')
    question_type = models.PositiveSmallIntegerField(choices=QUESTION_TYPES)
    question_text = models.TextField(max_length=255)
    mandatory = models.BooleanField(default=False)
    relative_index = models.IntegerField(default=1)


class Option(BasisModel):
    question = models.ForeignKey(Question, related_name='options')
    option_text = models.TextField(max_length=255)


class Submission(BasisModel):
    user = models.ForeignKey(User, related_name='surveys')
    survey = models.ForeignKey(Survey, related_name='submissions')

    class Meta:
        unique_together = ('survey', 'user')


class Answer(BasisModel):
    submission = models.ForeignKey(Submission, related_name='answers')
    question = models.ForeignKey(Question, related_name='answers')
    selected_options = models.ManyToManyField(Option, related_name='selected_in_answers',
                                              blank=True)
    answer_text = models.TextField(max_length=255, blank=True, null=True)

    def create(submission, question, **kwargs):
        selected_options = kwargs.pop('selected_options')
        answer = Answer.objects.create(submission=submission, question=question, **kwargs)
        answer.save()
        for selected_option in selected_options:
            answer.selected_options.add(selected_option)
        answer.save()
