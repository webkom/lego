from rest_framework import serializers

from lego.apps.events.serializers.events import EventReadSerializer
from lego.apps.survey.constants import QUESTION_TYPES
from lego.apps.survey.models import Alternative, Answer, Question, Submission, Survey
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class QuestionSerializer(BasisModelSerializer):
    question_type = serializers.ChoiceField(choices=QUESTION_TYPES)

    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question_text',  'mandatory')

    def create(self, validated_data):
        survey = Survey.objects.get(pk=self.context['view'].kwargs['survey_pk'])
        question = Question.objects.create(survey=survey, **validated_data)
        question.relative_index = question.survey.questions.count() + 1
        question.save()
        return question


class AlternativeSerializer(BasisModelSerializer):

    class Meta:
        model = Alternative
        fields = ('id', 'alternative_text', 'alternative_type')

    def create(self, validated_data):
        question = Question.objects.get(pk=self.context['view'].kwargs['question_pk'])
        alternative = Alternative.objects.create(question=question, **validated_data)
        return alternative

    def validate_alternative_type(self, value):
        question = Question.objects.get(pk=self.context['view'].kwargs['question_pk'])
        if question.question_type == 1 and value == 1:
            return value
        elif question.question_type == 2 and value in [2, 3]:
            return value
        elif question.question_type == 3 and value == 3:
            return value
        raise serializers.ValidationError('This alternative type does not match the question type')


class AnswerSerializer(BasisModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'submission', 'question', 'answer_text', 'selected_answers')


class SurveyReadSerializer(BasisModelSerializer):
    event = EventReadSerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'event')


class SubmissionReadSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    survey = SurveyReadSerializer()

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'submitted', 'submitted_time')


class SubmissionReadDetailedSerializer(BasisModelSerializer):
    user = PublicUserSerializer()
    survey = SurveyReadSerializer()
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'submitted', 'submitted_time', 'answers')


class SubmissionCreateAndUpdateSerializer(BasisModelSerializer):
    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'answers')

    def create(self, validated_data):
        survey = Survey.objects.get(pk=self.context['view'].kwargs['survey_pk'])
        submission = Submission.objects.create(survey=survey, user=validated_data['user'])
        submission.save()

        answers = validated_data['answers']
        for answer in answers:
            question = Question.objects.get(pk=answer['question'])
            new_answer = Answer.objects.create(submission=getattr(submission, 'id'), question=getattr(question, 'id'))
            new_answer.save()

        return submission


class SurveyReadDetailedSerializer(BasisModelSerializer):
    submissions = SubmissionReadDetailedSerializer(many=True)
    questions = QuestionSerializer(many=True)
    event = EventReadSerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'questions',
                  'submissions', 'event', 'template_type')


class SurveyCreateAndUpdateSerializer(BasisModelSerializer):
    is_clone = serializers.BooleanField()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'is_clone', 'event')

    def create(self, validated_data):
        is_clone = validated_data['is_clone']
        event = validated_data['event']
        if is_clone:
            template = Survey.objects.get(template_type=event.event_type)
            return template.copy(event, validated_data)
        return Survey.objects.create(**validated_data)
