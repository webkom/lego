from copy import deepcopy

from django.db import models
from django.utils import timezone

from lego.apps.events.constants import EVENT_TYPES
from lego.apps.survey.constants import ALTERNATIVE_TYPES, QUESTION_TYPES
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class Survey(BasisModel):
    title = models.CharField(max_length=100)
    active_from = models.DateTimeField(default=timezone.now)
    template_type = models.CharField(max_length=30, choices=EVENT_TYPES, null=True, blank=True)
    is_clone = models.BooleanField(default=False)
    event = models.OneToOneField('events.Event')

    @property
    def is_template(self):
        return self.template_type is not None

    def copy(self, event, validated_data):
        new_survey = Survey.objects.create(event=event, **validated_data)

        for question in self.questions.all():
            copied_q = deepcopy(question)
            copied_q.id = None
            copied_q.survey = new_survey
            copied_q.save()

            for alternative in question.alternatives.all().reverse():
                copied_a = deepcopy(alternative)
                copied_a.id = None
                copied_a.question = copied_q
                copied_a.save()

    def number_of_submissions(self):
        return self.submissions.filter(submitted=True).count()

    def is_answered_by_someone(self):
        if self.number_of_submissions():
            return True
        return False


class Question(BasisModel):

    class Meta:
        ordering = ['relative_index']

    survey = models.ForeignKey(Survey, related_name='questions')
    question_type = models.PositiveSmallIntegerField(choices=QUESTION_TYPES)
    question_text = models.TextField(max_length=255)
    mandatory = models.BooleanField(default=False)
    relative_index = models.IntegerField(null=True)


class Alternative(BasisModel):
    question = models.ForeignKey(Question, related_name='alternatives')
    alternative_text = models.TextField(max_length=255)
    alternative_type = models.PositiveSmallIntegerField(choices=ALTERNATIVE_TYPES, default=1)


class Submission(BasisModel):
    user = models.ForeignKey(User, related_name='surveys')
    survey = models.ForeignKey(Survey, related_name='submissions')
    submitted_time = models.DateTimeField(null=True)
    submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('survey', 'user')

    def submit(self):
        self.submitted = True
        self.submitted_time = timezone.now()
        self.save()


class Answer(BasisModel):
    submission = models.ForeignKey(Submission, related_name='answers')
    question = models.ForeignKey(Question, related_name='answers')
    selected_answers = models.ForeignKey(Alternative, related_name='answers', blank=True, null=True)
    answer_text = models.TextField(max_length=255, blank=True, null=True)
