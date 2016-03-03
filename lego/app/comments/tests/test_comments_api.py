from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.app.articles.models import Article
from lego.app.comments.models import Comment
from lego.users.models import AbakusGroup, User


def _get_list_url():
    return reverse('api:v1:comment-list')


def _get_detail_url(pk):
    return reverse('api:v1:comment-detail', kwargs={'pk': pk})


class ListCommentsAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_comments.yaml']

    def setUp(self):
        self.all_comments = Comment.objects.all()
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username='useradmin_test')
        self.comments_test_group = AbakusGroup.objects.get(name='CommentTest')
        self.comments_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(pk=self.with_permission.pk).first()

    def test_without_auth(self):
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 403)

    def test_with_authed_user(self):
        self.client.force_authenticate(user=self.with_permission)
        response = self.client.get(_get_list_url())
        self.assertEqual(response.status_code, 200)

        for comment in response.data:
            keys = set(comment.keys())
            self.assertEqual(
                keys,
                set(['id', 'text', 'author', 'createdAt', 'updatedAt', 'parent'])
            )


class RetrieveCommentsAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml', 'test_comments.yaml']

    def setUp(self):
        self.all_comments = Comment.objects.all()
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username='useradmin_test')
        self.comments_test_group = AbakusGroup.objects.get(name='CommentTest')
        self.comments_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(pk=self.with_permission.pk).first()
        self.test_comment = self.all_comments.first()

    def test_without_auth(self):
        pass
        # response = self.client.get(_get_detail_url(self.all_comments.first().pk))
        # self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        pass
        # self.client.force_authenticate(user=self.without_permission)
        # response = self.client.get(_get_detail_url(self.test_comment.pk))

        # self.assertEqual(response.status_code, 403)

    def test_with_authed_user(self):
        self.client.force_authenticate(user=self.with_permission)
        response = self.client.get(_get_detail_url(self.test_comment.pk))
        comment = response.data
        keys = set(comment.keys())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(keys, set(['id', 'text', 'author', 'created_at', 'updated_at', 'parent']))


class CreateCommentsAPITestCase(APITestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml', 'test_comments.yaml'
    ]

    def setUp(self):
        self.all_comments = Comment.objects.all()
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username='useradmin_test')
        self.comments_test_group = AbakusGroup.objects.get(name='CommentTest')
        self.comments_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(pk=self.with_permission.pk).first()

        '''
        self._test_comment_data = _test_comment_data.copy()
        self._test_comment_data['content_type'] = self._test_comment_data['content_type'].pk
        '''

    def test_without_auth(self):
        postData = {
            'text': 'Hey',
            'comment_target': '{0}-{1}'.format(
                ContentType.objects.get_for_model(Article).app_label,
                Article.objects.first().pk
            )
        }
        response = self.client.post(_get_list_url(), postData)

        self.assertEqual(response.status_code, 401)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_permission)
        postData = {
            'text': 'Hey',
            'comment_target': '{0}-{1}'.format(
                ContentType.objects.get_for_model(Article).app_label,
                Article.objects.first().pk
            )
        }
        response = self.client.post(_get_list_url(), postData)

        self.assertEqual(response.status_code, 403)

    def test_with_authed_user(self):
        self.client.force_authenticate(user=self.with_permission)
        postData = {
            'text': 'Hey',
            'comment_target': '{0}-{1}'.format(
                ContentType.objects.get_for_model(Article).app_label,
                Article.objects.first().pk
            )
        }
        response = self.client.post(_get_list_url(), postData)

        self.assertEqual(response.status_code, 201)

        comment = Comment.objects.get(pk=response.data['id'])

        self.assertEqual(comment.text, postData['text'])
        self.assertEqual(comment.created_by.pk, self.with_permission.pk)
        self.assertEqual(response.status_code, 201)

    def test_with_empty_text_and_source(self):
        self.client.force_authenticate(user=self.with_permission)
        postData = {
            'text': '',
            'comment_target': ''
        }
        response = self.client.post(_get_list_url(), postData)

        self.assertIn('comment_target', response.data.keys())
        self.assertIn('text', response.data.keys())
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_contenttype(self):
        self.client.force_authenticate(user=self.with_permission)
        postData = {
            'text': 'Hey',
            'comment_target': '{0}-{1}'.format(
                ContentType.objects.get_for_model(Article).app_label+'xyz',
                Article.objects.first().pk
            )
        }
        response = self.client.post(_get_list_url(), postData)

        self.assertIn('comment_target', response.data.keys())
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_objectid(self):
        self.client.force_authenticate(user=self.with_permission)
        postData = {
            'text': 'Hey',
            'comment_target': '{0}-{1}'.format(
                ContentType.objects.get_for_model(Article).app_label,
                Article.objects.last().pk+1000
            ),
        }
        response = self.client.post(_get_list_url(), postData)

        self.assertIn('comment_target', response.data.keys())
        self.assertEqual(response.status_code, 400)

    def test_with_parent(self):
        self.client.force_authenticate(user=self.with_permission)
        comment_target = '{0}-{1}'.format(
            ContentType.objects.get_for_model(Article).app_label,
            Article.objects.last().pk
        )

        response = self.client.post(_get_list_url(), {
            'comment_target': comment_target,
            'text': 'first comment'
        })
        self.assertEqual(response.status_code, 201)
        pk = response.data['id']

        response2 = self.client.post(_get_list_url(), {
            'comment_target': comment_target,
            'text': 'second comment',
            'parent': pk
        })
        self.assertEqual(response2.status_code, 201)

    def test_with_invalid_parent(self):
        pass

    def test_with_nonexistent_parent(self):
        pass


'''
class UpdateCommentsAPITestCase(APITestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml', 'test_comments.yaml'
    ]

    modified_comment = {
        'text': 'whats up'
    }

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

    def successful_update(self, updater, update_object):
        self.client.force_authenticate(user=updater)
        response = self.client.put(_get_detail_url(update_object.username), self.modified_user)
        user = User.objects.get(pk=update_object.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data.keys()), set(DetailedUserSerializer.Meta.fields))

        for key, value in self.modified_user.items():
            self.assertEqual(getattr(user, key), value)

    def test_self(self):
        self.successful_update(self.without_perm, self.without_perm)

    def test_with_useradmin(self):
        self.successful_update(self.with_perm, self.test_user)

    def test_other_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.put(_get_detail_url(self.test_user.username), self.modified_user)
        user = User.objects.get(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(user, self.test_user)

    def test_update_with_super_user(self):
        self.successful_update(self.with_perm, self.test_user)


class DeleteUsersAPITestCase(APITestCase):
    fixtures = ['test_abakus_groups.yaml', 'test_users.yaml']

    _test_user_data = {
        'username': 'new_testuser',
        'first_name': 'new',
        'last_name': 'test_user',
        'email': 'new@testuser.com',
    }

    def setUp(self):
        self.all_users = User.objects.all()

        self.with_perm = self.all_users.get(username='useradmin_test')
        self.useradmin_test_group = AbakusGroup.objects.get(name='UserAdminTest')
        self.useradmin_test_group.add_user(self.with_perm)
        self.without_perm = self.all_users.exclude(pk=self.with_perm.pk).first()

        self.test_user = get_test_user()

    def successful_delete(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.delete(_get_detail_url(self.test_user.username))

        self.assertEqual(response.status_code, 204)
        self.assertRaises(User.DoesNotExist, User.objects.get, pk=self.test_user.pk)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_perm)
        response = self.client.delete(_get_detail_url(self.test_user.username))
        users = User.objects.filter(pk=self.test_user.pk)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(len(users))

    def test_with_useradmin(self):
        self.successful_delete(self.with_perm)


class RetrieveSelfTestCase(APITestCase):
    fixtures = ['test_users.yaml']

    def setUp(self):
        self.user = User.objects.get(pk=1)

    def test_self_authed(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('api:v1:user-me'))

        self.assertEqual(response.status_code, 200)
        for field in DetailedUserSerializer.Meta.fields:
            self.assertEqual(getattr(self.user, field), response.data[field])

    def test_self_unauthed(self):
        response = self.client.get(reverse('api:v1:user-me'))
        self.assertEqual(response.status_code, 401)
'''
