from django.core import signing
from django.db.transaction import atomic
from rest_framework import exceptions, serializers

from lego.apps.events.serializers.events import EventForSurveySerializer
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
    event = EventForSurveySerializer()

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'event', 'template_type')


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

    @atomic
    def create(self, validated_data):
        survey = Survey.objects.get(pk=self.context['view'].kwargs['survey_pk'])
        answers = None if 'answers' not in validated_data else validated_data.pop('answers')
        submission = Submission.objects.create(survey=survey, **validated_data)

        if answers is not None:
            for answer in answers:
                question = answer.pop('question')

                if question.question_type is 'SINGLE_CHOICE' and \
                        len(answer['selected_options']) is not 1:
                    raise exceptions.ValidationError('You must select exactly one option')

                Answer.create(submission=submission, question=question, **answer)

        return submission


class SurveyReadDetailedSerializer(BasisModelSerializer):
    questions = QuestionSerializer(many=True)
    event = EventForSurveySerializer()

    class Meta:
        model = Survey
        # TODO: make new admin serializer for token
        fields = ('id', 'title', 'active_from', 'questions', 'event', 'template_type', 'token')


class SurveyCreateSerializer(BasisModelSerializer):
    questions = QuestionSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = Survey
        fields = ('id', 'title', 'active_from', 'template_type', 'event', 'questions')

    @atomic
    def create(self, validated_data):
        questions = validated_data.pop('questions')
        """
        request = self.context.get('request', None)
        token = signing.dumps({'user_id': request.user.id, 'survey_id': validated_data.get('id')})
        """
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

    @atomic
    def update(self, instance, validated_data):
        questions = validated_data.pop('questions')

        # Update the regular survey fields that aren't questions or options first
        super().update(instance, validated_data)

        # Delete questions that aren't in the received list
        for old_question in instance.questions.all():
            questions_with_ids = filter(lambda q: 'id' in q, questions)
            existing_question_ids = map(lambda q: q['id'], questions_with_ids)
            if old_question.id not in existing_question_ids:
                old_question.delete()

        # Add or update question, depending on whether the received option has an id
        for question in questions:
            options = question.pop('options') if 'options' in question else None
            if 'id' in question:
                Question.objects.filter(id=question['id']).update(**question)
                new_question = Question.objects.get(id=question['id'])
            else:
                new_question = Question.objects.create(survey=instance, **question)

            # Add or update option, depending on whether the received option has an id
            if options is not None:
                # Delete options that aren't in the received list
                for old_option in new_question.options.all():
                    options_with_ids = filter(lambda o: 'id' in o, options)
                    new_option_ids = map(lambda o: o['id'], options_with_ids)
                    if old_option.id not in new_option_ids:
                        old_option.delete()

                for option in options:
                    if 'id' in option:
                        Option.objects.filter(id=option['id']).update(**option)
                    else:
                        Option.objects.create(question=new_question, **option)

        return instance
