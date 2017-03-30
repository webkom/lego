from rest_framework import serializers

from lego.apps.events.serializers import EventReadSerializer
from lego.apps.survey.models import Survey, Question, Alternative, Submission, Answer
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer

class SurveyReadSerializer(BasisModelSerializer):
    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from')


class QuestionSerializer(BasisModelSerializer):
    survey = SurveyReadSerializer()
    question_type = serializers.ChoiceField(choices=Question.QUESTION_TYPES)

    class Meta:
        model = Question
        fields = ('id', 'survey', 'question_type', 'question_text', 'mandatory')


class AlternativeSerializer(BasisModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = Alternative
        fields = ('id', 'question', 'alternative_text', 'alternative_type')

class SubmissionReadSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    survey = SurveyReadSerializer()

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'submitted', 'submitted_time')


class AnswerSerializer(BasisModelSerializer):
    submission = SubmissionReadSerializer()
    alternative = AlternativeSerializer()

    class Meta:
        model = Answer
        fields = ('id', 'submission', 'alternative', 'answer_text')


class SurveyReadDetailedSerializer(BasisModelSerializer):
    submissions = SubmissionReadSerializer(many=True)
    questions = QuestionSerializer(many=True)
    event = EventReadSerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'questions', 'submissions', 'event')


class SubmissionReadDetailedSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    survey = SurveyReadSerializer()
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'submitted', 'submitted_time', 'answers')
