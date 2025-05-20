from random import shuffle

from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

from lego.apps.events.constants import EVENT_TYPES
from lego.apps.surveys.constants import (
    DISPLAY_TYPES,
    PIE_CHART,
    QUESTION_TYPES,
    TEXT_FIELD,
)
from lego.apps.surveys.permissions import (
    SubmissionPermissionHandler,
    SurveyPermissionHandler,
)
from lego.apps.users.models import User
from lego.utils.models import BasisModel


def generate_new_token():
    return get_random_string(length=64)


class Survey(BasisModel):
    title = models.CharField(max_length=100)
    active_from = models.DateTimeField(default=timezone.now)
    template_type = models.CharField(
        max_length=30, choices=EVENT_TYPES, null=True, blank=True, unique=False
    )
    is_template = models.BooleanField(default=False, null=False)
    event = models.OneToOneField(
        "events.Event", on_delete=models.CASCADE, null=True, blank=True
    )
    sent = models.BooleanField(default=False)
    token = models.CharField(
        max_length=64, default=None, unique=True, null=True, blank=True
    )

    class Meta:
        permission_handler = SurveyPermissionHandler()

    def aggregate_submissions(self):
        result = {}
        submissions = Submission.objects.filter(survey=self)
        for question in self.questions.all():
            options = {}
            if question.question_type == TEXT_FIELD:
                text_answers: list[str] = [
                    answer.answer_text
                    for answer in (
                        Answer.objects.filter(question=question).exclude(
                            hide_from_public=True
                        )
                    )
                ]
                shuffle(text_answers)
                options["answers"] = text_answers
            else:
                for option in question.options.all():
                    number_of_selections = submissions.filter(
                        answers__selected_options__in=[option.id]
                    ).count()
                    options[str(option.id)] = number_of_selections
            options["questionType"] = question.question_type
            result[str(question.id)] = options
        return result

    def generate_token(self):
        self.token = generate_new_token()
        self.save()

    def delete_token(self):
        self.token = None
        self.save()


class Question(models.Model):
    class Meta:
        ordering = ["relative_index"]

    survey = models.ForeignKey(
        Survey, related_name="questions", on_delete=models.CASCADE
    )
    # Save type of graph used
    display_type = models.CharField(
        max_length=64, choices=DISPLAY_TYPES, default=PIE_CHART
    )
    question_type = models.CharField(max_length=64, choices=QUESTION_TYPES)
    question_text = models.TextField(max_length=255)
    mandatory = models.BooleanField(default=False)
    relative_index = models.IntegerField(default=1)


class Option(models.Model):
    question = models.ForeignKey(
        Question, related_name="options", on_delete=models.CASCADE
    )
    option_text = models.TextField(max_length=255, default="")


class Submission(BasisModel):
    user = models.ForeignKey(User, related_name="surveys", on_delete=models.CASCADE)
    survey = models.ForeignKey(
        Survey, related_name="submissions", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("survey", "user")
        permission_handler = SubmissionPermissionHandler()


class Answer(BasisModel):
    submission = models.ForeignKey(
        Submission, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    selected_options = models.ManyToManyField(
        Option, related_name="selected_in_answers", blank=True
    )
    answer_text = models.TextField(default="", blank=True)
    hide_from_public = models.BooleanField(default=False)

    @classmethod
    def create(cls, submission, question, **kwargs):
        selected_options = kwargs.pop("selected_options")
        answer = Answer.objects.create(
            submission=submission, question=question, **kwargs
        )
        for selected_option in selected_options:
            answer.selected_options.add(selected_option)
        answer.save()

    def hide(self):
        self.hide_from_public = True
        self.save()

    def show(self):
        self.hide_from_public = False
        self.save()
