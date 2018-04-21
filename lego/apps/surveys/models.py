from django.db import models
from django.utils import timezone

from lego.apps.events.constants import EVENT_TYPES
from lego.apps.surveys.constants import QUESTION_TYPES
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class Survey(BasisModel):
    title = models.CharField(max_length=100)
    active_from = models.DateTimeField(default=timezone.now)
    template_type = models.CharField(
        max_length=30, choices=EVENT_TYPES, null=True, blank=True, unique=True
    )
    event = models.OneToOneField('events.Event', on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)
    token = models.CharField(max_length=255, null=True)


class Question(models.Model):
    class Meta:
        ordering = ['relative_index']
        unique_together = ('survey', 'relative_index')

    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)
    question_type = models.CharField(max_length=64, choices=QUESTION_TYPES)
    question_text = models.TextField(max_length=255)
    mandatory = models.BooleanField(default=False)
    relative_index = models.IntegerField(default=1)


class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    option_text = models.TextField(max_length=255, default='')


class Submission(BasisModel):
    user = models.ForeignKey(User, related_name='surveys', on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, related_name='submissions', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('survey', 'user')


class Answer(BasisModel):
    submission = models.ForeignKey(Submission, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(
        Option, related_name='selected_in_answers', blank=True
    )
    answer_text = models.TextField(max_length=255, blank=True, default="")

    def create(submission, question, **kwargs):
        selected_options = kwargs.pop('selected_options')
        answer = Answer.objects.create(submission=submission, question=question, **kwargs)
        for selected_option in selected_options:
            answer.selected_options.add(selected_option)
        answer.save()
