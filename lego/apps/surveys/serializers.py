from rest_framework import exceptions, serializers

from lego.apps.events.serializers.events import EventReadSerializer
from lego.apps.surveys.constants import QUESTION_TYPES
from lego.apps.surveys.models import Answer, Option, Question, Submission, Survey
# from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class OptionSerializer(BasisModelSerializer):

    class Meta:
        model = Option
        fields = ('id', 'option_text')


class QuestionSerializer(BasisModelSerializer):
    question_type = serializers.ChoiceField(choices=QUESTION_TYPES)
    options = OptionSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question_text', 'mandatory', 'options')


class AnswerSerializer(BasisModelSerializer):
    question = QuestionSerializer()
    selected_options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Answer
        fields = ('id', 'submission', 'question', 'answer_text', 'selected_options')


class AnswerCreateAndUpdateSerializer(BasisModelSerializer):

    class Meta:
        model = Answer
        fields = ('id', 'question', 'answer_text', 'selected_options')


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
    # Not any different from list serializer atm. Should some info only be showed in detail?
    # user = PublicUserSerializer()
    # survey = SurveyReadSerializer()
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
        answers = None if 'answers' not in validated_data else validated_data.pop('answers')
        submission = Submission.objects.create(survey=survey, **validated_data)
        submission.save()

        if answers is not None:
            for answer in answers:
                question = answer.pop('question')

                if getattr(question, 'question_type') in [1, 2]:
                    if getattr(question, 'question_type') is 1 and \
                                    len(answer['selected_options']) > 1:
                        raise exceptions.ValidationError('You cannot select multiple options for '
                                                         'this type of question.')

                    Answer.create(submission, question, **answer)
                else:
                    new_answer = Answer.objects.create(submission=submission, question=question,
                                                       **answer)
                    new_answer.save()

        return submission


class SurveyReadDetailedSerializer(BasisModelSerializer):
    questions = QuestionSerializer(many=True)
    event = EventReadSerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'questions', 'event', 'template_type')


class SurveyCreateAndUpdateSerializer(BasisModelSerializer):
    is_clone = serializers.BooleanField()
    questions = QuestionSerializer(many=True, required=False, allow_null=True)

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
            options = None
            if 'options' in question:
                options = question.pop('options')
            new_question = Question.objects.create(survey=survey, **question)
            new_question.save()

            if options is not None:
                for option in options:
                    new_option = Option.objects.create(question=new_question, **option)
                    new_option.save()

        return survey
