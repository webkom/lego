from rest_framework import exceptions, serializers

from lego.apps.events.serializers.events import EventReadSerializer
from lego.apps.surveys.constants import QUESTION_TYPES
from lego.apps.surveys.models import Answer, Option, Question, Submission, Survey
from lego.apps.users.serializers.users import PublicUserSerializer
from lego.utils.serializers import BasisModelSerializer


class OptionSerializer(BasisModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'option_text')


class OptionUpdateSerializer(BasisModelSerializer):
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = Option
        fields = ('id', 'option_text')


class QuestionSerializer(BasisModelSerializer):
    question_type = serializers.ChoiceField(choices=QUESTION_TYPES)
    options = OptionSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question_text', 'mandatory', 'options', 'relative_index')


class QuestionUpdateSerializer(BasisModelSerializer):
    question_type = serializers.ChoiceField(choices=QUESTION_TYPES)
    options = OptionUpdateSerializer(many=True, required=False, allow_null=True)
    id = serializers.IntegerField(read_only=False)

    class Meta:
        model = Question
        fields = ('id', 'question_type', 'question_text', 'mandatory', 'options', 'relative_index')


class AnswerSerializer(BasisModelSerializer):
    question = QuestionSerializer()

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
        fields = ('id', 'title', 'active_from', 'event', 'is_template')


class SubmissionReadSerializer(BasisModelSerializer):
    answers = AnswerSerializer(many=True)
    user = PublicUserSerializer()

    class Meta:
        model = Submission
        fields = ('id', 'user', 'survey', 'answers')


class SubmissionCreateAndUpdateSerializer(BasisModelSerializer):
    answers = AnswerCreateAndUpdateSerializer(many=True)

    class Meta:
        model = Submission
        fields = ('id', 'user', 'answers')

    def create(self, validated_data):
        survey = Survey.objects.get(pk=self.context['view'].kwargs['survey_pk'])
        answers = None if 'answers' not in validated_data else validated_data.pop('answers')
        submission = Submission.objects.create(survey=survey, **validated_data)

        if answers is not None:
            for answer in answers:
                question = answer.pop('question')

                if getattr(question, 'question_type') is QUESTION_TYPES.SINGLE_CHOICE and \
                        len(answer['selected_options']) > 1:
                    raise exceptions.ValidationError(
                        'You cannot select multiple options for '
                        'this type of question.'
                    )

                Answer.objects.create(submission=submission, question=question, **answer)

        return submission


class SurveyReadDetailedSerializer(BasisModelSerializer):
    questions = QuestionSerializer(many=True)
    event = EventReadSerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'questions', 'event', 'template_type')


class SurveyCreateSerializer(BasisModelSerializer):
    questions = QuestionSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'template_type', 'event', 'questions')

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        survey = Survey.objects.create(**validated_data)

        for question in questions:
            options = question.pop('options') if 'options' in question else None
            new_question = Question.objects.create(survey=survey, **question)

            if options is not None:
                for option in options:
                    Option.objects.create(question=new_question, **option)

        return survey


class SurveyUpdateSerializer(BasisModelSerializer):
    questions = QuestionUpdateSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'template_type', 'event', 'questions')

    def update(self, instance, validated_data):
        questions = validated_data.pop('questions')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        for question in questions:
            options = question.pop('options') if 'options' in question else None
            if 'id' in question:
                Question.objects.filter(id=question['id']).update(**question)
            else:
                new_question = Question.objects.create(survey=instance, **question)

            if options is not None:
                for option in options:
                    if 'id' in option:
                        Option.objects.filter(id=option['id']).update(**option)
                    else:
                        Option.objects.create(question=new_question, **option)

        return instance
