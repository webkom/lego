from unittest import mock

from django.urls import reverse

from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, User
from lego.apps.users.registrations import Registrations
from lego.utils.test_utils import BaseAPITestCase


def _get_list_request_url():
    return reverse('api:v1:student-confirmation-request-list')


def _get_list_perform_url():
    return reverse('api:v1:student-confirmation-perform-list')


def _get_student_confirmation_token_request_url(token):
    return f'{_get_list_request_url()}?token={token}'


def _get_student_confirmation_token_perform_url(token):
    return f'{_get_list_perform_url()}?token={token}'


class RetrieveStudentConfirmationAPITestCase(BaseAPITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.user_with_student_confirmation = User.objects.get(username='test1')
        self.user_without_student_confirmation = User.objects.get(username='test2')

    def test_with_unauthenticated_user(self):
        response = self.client.get(_get_list_request_url())
        self.assertEqual(response.status_code, 401)

    def test_without_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.get(_get_list_request_url())
        self.assertEqual(response.status_code, 400)

    def test_with_empty_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.get(_get_student_confirmation_token_request_url(''))
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.get(_get_student_confirmation_token_request_url('InvalidToken'))
        self.assertEqual(response.status_code, 400)

    def test_with_valid_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.get(
            _get_student_confirmation_token_request_url(
                Registrations.generate_student_confirmation_token(
                    'teststudentusername', constants.DATA, True
                )
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('student_username'), 'teststudentusername')
        self.assertEqual(response.data.get('course'), constants.DATA)
        self.assertEqual(response.data.get('member'), True)

    def test_with_valid_token_and_capitalized_student_username(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.get(
            _get_student_confirmation_token_request_url(
                Registrations.generate_student_confirmation_token(
                    'TestStudentUsername', constants.DATA, True
                )
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('student_username'), 'teststudentusername')
        self.assertEqual(response.data.get('course'), constants.DATA)
        self.assertEqual(response.data.get('member'), True)


class CreateStudentConfirmationAPITestCase(BaseAPITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    _test_student_confirmation_data = {
        'student_username': 'newteststudentusername',
        'course': constants.DATA,
        'member': True,
        'captcha_response': 'testCaptcha'
    }

    def setUp(self):
        grade = AbakusGroup.objects.create(
            name=constants.FIRST_GRADE_DATA, type=constants.GROUP_GRADE
        )
        self.user_with_student_confirmation = User.objects.get(username='test1')
        grade.add_user(self.user_with_student_confirmation)
        self.user_without_student_confirmation = User.objects.get(username='test2')

    def test_with_unauthenticated_user(self):
        response = self.client.post(_get_list_request_url())
        self.assertEqual(response.status_code, 401)

    def test_without_data(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_list_request_url())
        self.assertEqual(response.status_code, 400)

    @mock.patch(
        'lego.apps.users.serializers.student_confirmation.verify_captcha', return_value=True
    )
    def test_with_existing_data(self, *args):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(
            _get_list_request_url(), {
                'student_username': 'test1student',
                'course': constants.DATA,
                'member': True,
                'captcha_response': 'testCaptcha'
            }
        )
        self.assertEqual(response.status_code, 400)

    @mock.patch(
        'lego.apps.users.serializers.student_confirmation.verify_captcha', return_value=True
    )
    def test_with_invalid_data_keys(self, *args):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(
            _get_list_request_url(), {
                'wrong_username': 'newteststudentusername',
                'wrong_course': constants.DATA,
                'wrong_member': True,
                'wrong_captcha_response': 'testCaptcha'
            }
        )
        self.assertEqual(response.status_code, 400)

    @mock.patch(
        'lego.apps.users.serializers.student_confirmation.verify_captcha', return_value=True
    )
    def test_with_invalid_student_username(self, *args):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        invalid_data = self._test_student_confirmation_data.copy()
        invalid_data['student_username'] = 'test_u$er@'
        response = self.client.post(_get_list_request_url(), invalid_data)
        self.assertEqual(response.status_code, 400)

    @mock.patch(
        'lego.apps.users.serializers.student_confirmation.verify_captcha', return_value=True
    )
    def test_with_invalid_course(self, *args):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        invalid_data = self._test_student_confirmation_data.copy()
        invalid_data['course'] = 'test'
        response = self.client.post(_get_list_request_url(), invalid_data)
        self.assertEqual(response.status_code, 400)

    @mock.patch(
        'lego.apps.users.serializers.student_confirmation.verify_captcha', return_value=True
    )
    def test_with_invalid_member_boolean(self, *args):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        invalid_data = self._test_student_confirmation_data.copy()
        invalid_data['member'] = 'test'
        response = self.client.post(_get_list_request_url(), invalid_data)
        self.assertEqual(response.status_code, 400)

    @mock.patch(
        'lego.apps.users.serializers.student_confirmation.verify_captcha', return_value=True
    )
    def test_with_already_confirmed_student_username(self, mock_verify_captcha):
        AbakusGroup.objects.get(name='Abakus').add_user(self.user_with_student_confirmation)
        self.client.force_authenticate(self.user_with_student_confirmation)
        response = self.client.post(_get_list_request_url(), self._test_student_confirmation_data)
        self.assertEqual(response.status_code, 400)

    @mock.patch(
        'lego.apps.users.serializers.student_confirmation.verify_captcha', return_value=False
    )
    def test_with_invalid_captcha(self, *args):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_list_request_url(), self._test_student_confirmation_data)
        self.assertEqual(response.status_code, 400)

    @mock.patch(
        'lego.apps.users.serializers.student_confirmation.verify_captcha', return_value=True
    )
    def test_with_valid_captcha(self, mock_verify_captcha):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_list_request_url(), self._test_student_confirmation_data)
        self.assertEqual(response.status_code, 204)


class UpdateStudentConfirmationAPITestCase(BaseAPITestCase):
    fixtures = ['initial_files.yaml', 'initial_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        grade = AbakusGroup.objects.get(name=constants.FIRST_GRADE_DATA)
        self.user_with_student_confirmation = User.objects.get(username='test1')
        grade.add_user(self.user_with_student_confirmation)
        self.user_with_student_confirmation = User.objects.get(username='test1')
        self.user_without_student_confirmation = User.objects.get(username='test2')
        self.user_with_grade_group_but_no_student_confirmation = User.objects.get(username='pleb')

    def create_token(
        self, student_username='newstudentusername', course=constants.DATA, member=True
    ):
        return Registrations.generate_student_confirmation_token(student_username, course, member)

    def test_without_authenticated_user(self):
        response = self.client.post(_get_student_confirmation_token_request_url('randomToken'))
        self.assertEqual(response.status_code, 401)

    def test_without_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_list_perform_url())
        self.assertEqual(response.status_code, 400)

    def test_with_empty_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_list_perform_url())
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_student_confirmation_token_perform_url('InvalidToken'))
        self.assertEqual(response.status_code, 400)

    def test_with_already_confirmed_student_username(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_with_student_confirmation)
        self.client.force_authenticate(self.user_with_student_confirmation)
        token = self.create_token()
        response = self.client.post(_get_student_confirmation_token_perform_url(token))
        self.assertEqual(response.status_code, 400)

    def test_without_abakus_member_checked_and_komtek_course(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        token = self.create_token(course=constants.KOMTEK, member=False)
        response = self.client.post(_get_student_confirmation_token_perform_url(token))
        self.assertEqual(response.status_code, 200)

        user = self.user_without_student_confirmation
        user_groups = user.all_groups
        self.assertEqual(user.student_username, 'newstudentusername')
        self.assertEqual(user.is_staff, False)

        # Test course groups
        course_group = AbakusGroup.objects.get(name=constants.KOMTEK_LONG)
        self.assertEqual(course_group in user_groups, True)
        grade_group = AbakusGroup.objects.get(name=constants.FIRST_GRADE_KOMTEK)
        self.assertEqual(grade_group in user_groups, True)

        # Test member group
        self.assertEqual(user.is_abakus_member, False)
        member_group = AbakusGroup.objects.get(name=constants.MEMBER_GROUP)
        self.assertEqual(member_group in user_groups, False)

    def test_with_already_in_grade_group_but_not_abakus(self):
        AbakusGroup.objects.get(name='Users').add_user(
            self.user_with_grade_group_but_no_student_confirmation
        )
        AbakusGroup.objects.get(name='2. klasse Kommunikasjonsteknologi').add_user(
            self.user_with_grade_group_but_no_student_confirmation
        )
        self.client.force_authenticate(self.user_with_grade_group_but_no_student_confirmation)
        token = self.create_token(course=constants.KOMTEK, member=True)
        response = self.client.post(_get_student_confirmation_token_perform_url(token))
        self.assertEqual(response.status_code, 200)

        user = self.user_with_grade_group_but_no_student_confirmation
        user_groups = user.all_groups
        self.assertEqual(user.student_username, 'newstudentusername')
        self.assertEqual(user.is_staff, False)

        # Test course groups
        course_group = AbakusGroup.objects.get(name=constants.KOMTEK_LONG)
        self.assertEqual(course_group in user_groups, True)
        grade_group = AbakusGroup.objects.get(name=constants.FIRST_GRADE_KOMTEK)
        self.assertEqual(grade_group in user_groups, False)
        grade_group = AbakusGroup.objects.get(name='2. klasse Kommunikasjonsteknologi')
        self.assertEqual(grade_group in user_groups, True)

        # Test member group
        self.assertEqual(user.is_abakus_member, True)
        member_group = AbakusGroup.objects.get(name=constants.MEMBER_GROUP)
        self.assertEqual(member_group in user_groups, True)

    def test_with_abakus_member_checked(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        token = self.create_token()
        response = self.client.post(_get_student_confirmation_token_perform_url(token))
        self.assertEqual(response.status_code, 200)

        user = self.user_without_student_confirmation
        user_groups = user.all_groups
        self.assertEqual(user.is_staff, False)

        # Test user data
        self.assertEqual(user.student_username, 'newstudentusername')
        self.assertEqual(user.is_staff, False)

        # Test course groups
        course_group = AbakusGroup.objects.get(name=constants.DATA_LONG)
        self.assertEqual(course_group in user_groups, True)
        grade_group = AbakusGroup.objects.get(name=constants.FIRST_GRADE_DATA)
        self.assertEqual(grade_group in user_groups, True)

        # Test member group
        self.assertEqual(user.is_abakus_member, True)
        member_group = AbakusGroup.objects.get(name=constants.MEMBER_GROUP)
        self.assertEqual(member_group in user_groups, True)
