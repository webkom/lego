from rest_framework import serializers

from lego.apps.events.serializers.events import EventReadSerializer
from lego.apps.survey.constants import QUESTION_TYPES
from lego.apps.survey.models import Alternative, Answer, Question, Submission, Survey
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class AlternativeSerializer(BasisModelSerializer):

    class Meta:
        model = Alternative
        fields = ('id', 'alternative_text', 'alternative_type')


class QuestionSerializer(BasisModelSerializer):
    question_type = serializers.ChoiceField(choices=QUESTION_TYPES)
    alternatives = AlternativeSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question_text',  'mandatory', 'alternatives')


class AnswerSerializer(BasisModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = Answer
        fields = ('id', 'submission', 'question', 'answer_text', 'selected_answers')


class AnswerCreateAndUpdateSerializer(BasisModelSerializer):

    class Meta:
        model = Answer
        fields = ('id', 'question', 'answer_text', 'selected_answers')


class SurveyReadSerializer(BasisModelSerializer):
    event = EventReadSerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'event')


class SubmissionReadSerializer(BasisModelSerializer):
    # Do we want user and survey as nested objects?
    # user = PublicUserSerializer()
    # survey = SurveyReadSerializer()
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'submitted', 'submitted_time', 'answers')


class SubmissionReadDetailedSerializer(BasisModelSerializer):
    # Not used atm, but might be used later. Should some info only be showed in detail?
    user = PublicUserSerializer()
    survey = SurveyReadSerializer()
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'submitted', 'submitted_time', 'answers')


class SubmissionCreateAndUpdateSerializer(BasisModelSerializer):
    answers = AnswerCreateAndUpdateSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'user', 'answers')

    def create(self, validated_data):
        survey = Survey.objects.get(pk=self.context['view'].kwargs['survey_pk'])
        answers = None
        if 'answers' in validated_data:
            answers = validated_data.pop('answers')
        submission = Submission.objects.create(survey=survey, **validated_data)
        submission.save()

        for answer in answers:
            question = Question.objects.get(id=getattr(answer.pop('question'), 'id'))
            new_answer = Answer.objects.create(submission=submission, question=question, **answer)
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
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'is_clone', 'event', 'questions')

    def create(self, validated_data):
        is_clone = validated_data['is_clone']
        event = validated_data['event']
        if is_clone:
            template = Survey.objects.get(template_type=event.event_type)
            return template.copy(event, validated_data)

        questions = validated_data.pop('questions')
        survey = Survey.objects.create(**validated_data)
        survey.save()

        for question in questions:
            alternatives = None
            if 'alternatives' in question:
                alternatives = question.pop('alternatives')
            new_question = Question.objects.create(survey=survey, **question)
            new_question.save()

            if alternatives is not None:
                for alternative in alternatives:
                    new_alternative = Alternative.objects.create(question=new_question,
                                                                 **alternative)
                    new_alternative.save()

        return survey
