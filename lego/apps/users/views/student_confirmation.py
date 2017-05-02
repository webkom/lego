from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from structlog import get_logger

from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, User
from lego.apps.users.serializers.student_confirmation import StudentConfirmationSerializer
from lego.apps.users.serializers.users import DetailedUserSerializer
from lego.utils.functions import verify_captcha
from lego.utils.tasks import send_email

log = get_logger()


class StudentConfirmationViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = StudentConfirmationSerializer
    permission_classes = (IsAuthenticated, )

    """
    Validates a student confirmation token.

    The request errors out if the token has expired or is invalid.
    Request URL: GET /api/v1/users/student-confirmation/?token=<token>
    """
    def get(self, request, pk=None, format=None):
        if not request.GET.get('token', False):
            raise ValidationError(detail='Student confirmation token is required.')
        student_confirmation = User.validate_student_confirmation_token(
            request.GET.get('token', False)
        )
        if student_confirmation is None:
            raise ValidationError(detail='Token expired or invalid.')
        return Response(student_confirmation, status=status.HTTP_200_OK)

    """
    Attempts to create a student confirmation token and email it to the user.
    """
    def create(self, request, *args, **kwargs):
        if request.data.get('student_username', None) is None:
            raise ValidationError('student_username needs to be set and not be empty')

        request.data['student_username'] = request.data['student_username'].lower()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not verify_captcha(serializer.validated_data.get('captcha_response', None)):
            raise ValidationError(detail='Bad captcha')

        user = request.user

        if user.student_username is not None:
            raise PermissionDenied(detail='Already confirmed a student username')

        student_username = serializer.data.get('student_username')

        token = User.generate_student_confirmation_token(
            student_username,
            serializer.data.get('course'),
            serializer.data.get('member')
        )

        send_email.delay(
            to_email=f'{student_username}@{constants.STUDENT_EMAIL_DOMAIN}',
            context={
                "token": token,
                "full_name": user.get_full_name(),
                "email_title": 'Bekreft student kontoen din på Abakus.no'
            },
            subject='Bekreft student kontoen din på Abakus.no',
            plain_template='users/email/student_confirmation.html',
            html_template='users/email/student_confirmation.txt',
            from_email=None
        )

        return Response(status=status.HTTP_202_ACCEPTED)

    """
    Attempts to confirm the student based on the student confirmation token.
    """
    def put(self, request, *args, **kwargs):
        if not request.GET.get('token', False):
            raise ValidationError(detail='Student confirmation token is required.')

        student_confirmation = User.validate_student_confirmation_token(
            request.GET.get('token', False)
        )

        user = request.user

        if user.student_username is not None:
            raise ValidationError(detail='Already confirmed a student username')

        serializer = self.get_serializer(data=student_confirmation)
        serializer.is_valid(raise_exception=True)

        user.student_username = serializer.validated_data.get('student_username')
        course = serializer.validated_data.get('course')

        if course == constants.DATA:
            course_group = AbakusGroup.objects.get(name=constants.DATA_LONG)
            course_group.add_user(user)

            grade_group = AbakusGroup.objects.get(name=constants.FIRST_GRADE_DATA)
            grade_group.add_user(user)
        else:
            course_group = AbakusGroup.objects.get(name=constants.KOMTEK_LONG)
            course_group.add_user(user)

            grade_group = AbakusGroup.objects.get(name=constants.FIRST_GRADE_KOMTEK)
            grade_group.add_user(user)

        if serializer.validated_data.get('member'):
            member_group = AbakusGroup.objects.get(name=constants.MEMBER_GROUP)
            member_group.add_user(user)

        user.save()

        return Response(DetailedUserSerializer(user).data, status=status.HTTP_202_ACCEPTED)
