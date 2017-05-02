from unittest import mock

from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase, APITransactionTestCase

from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup, User


def _get_list_url():
    return reverse('api:v1:student-confirmation-list')


def _get_student_confirmation_token_url(token):
    return f'{_get_list_url()}?token={token}'


class RetrieveStudentConfirmationAPITestCase(APITestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml']

    def setUp(self):
        self.user_with_student_confirmation = User.objects.get(username='test1')
        self.user_without_student_confirmation = User.objects.get(username='test2')

    def test_with_unauthenticated_user(self):
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 401)

    def test_without_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 400)

    def test_with_empty_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.get(_get_student_confirmation_token_url(''))
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.get(_get_student_confirmation_token_url('InvalidToken'))
        self.assertEqual(response.status_code, 400)

    def test_with_valid_token(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.get(
            _get_student_confirmation_token_url(
                User.generate_student_confirmation_token(
                    'teststudentusername',
                    constants.DATA,
                    True
                )
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('student_username'), 'teststudentusername')
        self.assertEqual(response.data.get('course'), constants.DATA)
        self.assertEqual(response.data.get('member'), True)


class CreateStudentConfirmationAPITestCase(APITransactionTestCase):
    fixtures = ['initial_abakus_groups.yaml', 'test_users.yaml']

    _test_student_confirmation_data = {
        'student_username': 'newteststudentusername',
        'course': constants.DATA,
        'member': True,
        'captcha_response': 'testCaptcha'
    }

    def setUp(self):
        self.user_with_student_confirmation = User.objects.get(username='test1')
        self.user_without_student_confirmation = User.objects.get(username='test2')

    def test_with_unauthenticated_user(self):
        response = self.client.post(_get_list_url())
        self.assertEqual(response.status_code, 401)

    def test_without_data(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_list_url())
        self.assertEqual(response.status_code, 400)

    def test_with_existing_data(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_list_url(), {
            'student_username': 'test1student',
            'course': constants.DATA,
            'member': True,
            'captcha_response': 'testCaptcha'
        })
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_data_keys(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_list_url(), {
            'wrong_username': 'newteststudentusername',
            'wrong_course': constants.DATA,
            'wrong_member': True,
            'wrong_captcha_response': 'testCaptcha'
        })
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_student_username(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        invalid_data = self._test_student_confirmation_data.copy()
        invalid_data['student_username'] = 'test_u$er@'
        response = self.client.post(_get_list_url(), invalid_data)
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_course(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        invalid_data = self._test_student_confirmation_data.copy()
        invalid_data['course'] = 'test'
        response = self.client.post(_get_list_url(), invalid_data)
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_member_boolean(self):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        invalid_data = self._test_student_confirmation_data.copy()
        invalid_data['member'] = 'test'
        response = self.client.post(_get_list_url(), invalid_data)
        self.assertEqual(response.status_code, 400)

    @mock.patch('lego.apps.users.views.student_confirmation.verify_captcha', return_value=True)
    def test_with_already_confirmed_user(self, mock_verify_captcha):
        AbakusGroup.objects.get(name='Abakus').add_user(self.user_with_student_confirmation)
        self.client.force_authenticate(self.user_with_student_confirmation)
        response = self.client.post(_get_list_url(), self._test_student_confirmation_data)
        self.assertEqual(response.status_code, 403)

    @mock.patch('lego.apps.users.views.student_confirmation.verify_captcha', return_value=False)
    def test_with_invalid_captcha(self, *args):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_list_url(), self._test_student_confirmation_data)
        self.assertEqual(response.status_code, 400)

    @mock.patch('lego.apps.users.views.student_confirmation.verify_captcha', return_value=True)
    def test_with_valid_captcha(self, mock_verify_captcha):
        AbakusGroup.objects.get(name='Users').add_user(self.user_without_student_confirmation)
        self.client.force_authenticate(self.user_without_student_confirmation)
        response = self.client.post(_get_list_url(), self._test_student_confirmation_data)
        self.assertEqual(response.status_code, 202)
