from django.db import models

from django.utils import timezone

from lego.apps.events.constants import EVENT_TYPES
from lego.apps.users.models import User
from lego.utils.models import BasisModel


class Survey(BasisModel):
    title = models.CharField(max_length=100)
    active_from = models.DateTimeField(default=timezone.now)
    template_type = models.CharField(max_length=30, choices=EVENT_TYPES, null=True, blank=True)

    @property
    def is_template(self):
        return self.template_type is not None

    def number_of_submissions(self):
        return self.submissions.filter(submitted=True).count()

    def is_answered_by_someone(self):
        if self.number_of_submissions():
            return True
        return False


class Question(BasisModel):

    class Meta:
        ordering = ['relative_index']

    QUESTION_TYPES = (
        (1, 'single_choice'),
        (2, 'multiple_choice'),
        (3, 'text_field')
    )

    survey = models.ForeignKey(Survey, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question_text = models.TextField(max_length=255)
    mandatory = models.BooleanField(default=False)
    relative_index = models.IntegerField(null=True)


class Alternative(BasisModel):
    question = models.ForeignKey(Question, related_name='alternatives')
    alternative_text = models.TextField(max_length=255)

    ALTERNATIVE_TYPES = (
        (1, 'radio_button'),
        (2, 'check_box'),
        (3, 'text_box'),
    )

    alternative_type = models.CharField(max_length=20, choices=ALTERNATIVE_TYPES, default = 1)


class Submission(BasisModel):
    user = models.ForeignKey(User, related_name='surveys')
    survey = models.ForeignKey(Survey, related_name='submissions')
    submitted_time = models.DateTimeField(null=True)
    submitted = models.BooleanField(default=False)

    def submit(self):
        self.submitted = True
        self.submitted_time = timezone.now()
        self.save()


class Answer(BasisModel):
    submission = models.ForeignKey(Submission, related_name='answers')
    alternative = models.ForeignKey(Alternative, related_name='answers')
    answer_text = models.TextField(max_length=255, blank=True)
