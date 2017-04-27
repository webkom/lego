from rest_framework import serializers

from lego.apps.events.models import Event
from lego.apps.events.serializers import EventReadSerializer
from lego.apps.survey.constants import QUESTION_TYPES
from lego.apps.survey.models import Alternative, Answer, Question, Submission, Survey
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class SurveyReadSerializer(BasisModelSerializer):
    event = EventReadSerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'event')


class QuestionSerializer(BasisModelSerializer):
    survey = SurveyReadSerializer()
    question_type = serializers.ChoiceField(choices=QUESTION_TYPES)

    class Meta:
        model = Question
        fields = ('id', 'survey', 'question_type', 'question_text', 'mandatory')

    def create(self, validated_data):
        question = Question.objects.create(**validated_data)
        question.relative_index = question.survey.questions.count() + 1
        question.save()
        return question


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
        fields = ('id', 'title', 'active_from', 'questions',
                  'submissions', 'event', 'template_type')


class SurveyCreateAndUpdateSerializer(BasisModelSerializer):
    is_clone = serializers.BooleanField()
    event_id = serializers.IntegerField()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'is_clone', 'event_id')

    def create(self, validated_data):
        print(validated_data)
        is_clone = validated_data['is_clone']
        event = Event.objects.get(id=validated_data.pop('event_id'))
        if is_clone:
            template = Survey.objects.get(template_type=event.event_type)
            return template.copy(event, validated_data)
        return Survey.objects.create(event=event, **validated_data)


class SubmissionReadDetailedSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    survey = SurveyReadSerializer()
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'submitted', 'submitted_time', 'answers')


class SubmissionCreateAndUpdateSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    survey = SubmissionReadSerializer()

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey')
