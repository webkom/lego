from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase

from lego.apps.articles.models import Article
from lego.apps.comments.models import Comment
from lego.apps.users.models import AbakusGroup, User


def _get_list_url():
    return reverse('api:v1:comment-list')


def _get_detail_url(pk):
    return reverse('api:v1:comment-detail', kwargs={'pk': pk})


class CreateCommentsAPITestCase(APITestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml'
    ]

    def setUp(self):
        self.all_comments = Comment.objects.all()
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username='useradmin_test')
        self.comments_test_group = AbakusGroup.objects.get(name='CommentTest')
        self.comments_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(pk=self.with_permission.pk).first()

    def test_without_auth(self):
        post_data = {
            'text': 'Hey',
            'comment_target': '{0}-{1}'.format(
                ContentType.objects.get_for_model(Article).app_label,
                Article.objects.first().pk
            )
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertEqual(response.status_code, 401)

    def test_without_view_permissions(self):
        self.client.force_authenticate(user=self.without_permission)
        post_data = {
            'text': 'Hey',
            'comment_target': '{0}-{1}'.format(
                ContentType.objects.get_for_model(Article).app_label,
                Article.objects.first().pk
            )
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertEqual(response.status_code, 403)

    def test_with_view_permissions(self):
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        post_data = {
            'text': 'Hey',
            'comment_target': '{0}.{1}-{2}'.format(
                content_type.app_label,
                content_type.model,
                Article.objects.first().pk
            )
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertEqual(response.status_code, 201)

        comment = Comment.objects.get(pk=response.data['id'])

        self.assertEqual(comment.text, post_data['text'])
        self.assertEqual(comment.created_by.pk, self.with_permission.pk)

    def test_with_empty_text_and_source(self):
        self.client.force_authenticate(user=self.with_permission)
        post_data = {
            'text': '',
            'comment_target': ''
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertIn('comment_target', response.data.keys())
        self.assertIn('text', response.data.keys())
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_contenttype(self):
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        post_data = {
            'text': 'Hey',
            'comment_target': '{0}.{1}-{2}'.format(
                content_type.app_label+'xyz',
                content_type.model,
                Article.objects.first().pk
            )
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertIn('comment_target', response.data.keys())
        self.assertEqual(response.status_code, 400)

    def test_with_invalid_objectid(self):
        self.client.force_authenticate(user=self.with_permission)
        post_data = {
            'text': 'Hey',
            'comment_target': '{0}-{1}'.format(
                ContentType.objects.get_for_model(Article).app_label,
                Article.objects.last().pk+1000
            ),
        }
        response = self.client.post(_get_list_url(), post_data)

        self.assertIn('comment_target', response.data.keys())
        self.assertEqual(response.status_code, 400)

    def test_with_parent(self):
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        comment_target = '{0}.{1}-{2}'.format(
            content_type.app_label,
            content_type.model,
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
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        comment_target = '{0}.{1}-{2}'.format(
            content_type.app_label,
            content_type.model,
            Article.objects.last().pk
        )
        comment_target_2 = '{0}.{1}-{2}'.format(
            content_type.app_label,
            content_type.model,
            Article.objects.first().pk
        )

        response = self.client.post(_get_list_url(), {
            'comment_target': comment_target,
            'text': 'first comment'
        })
        self.assertEqual(response.status_code, 201)
        pk = response.data['id']

        response2 = self.client.post(_get_list_url(), {
            'comment_target': comment_target_2,
            'text': 'second comment',
            'parent': pk
        })
        self.assertEqual(response2.status_code, 400)
        self.assertIn('parent', response2.data)

    def test_with_nonexistent_parent(self):
        self.client.force_authenticate(user=self.with_permission)
        content_type = ContentType.objects.get_for_model(Article)
        comment_target = '{0}.{1}-{2}'.format(
            content_type.app_label,
            content_type.model,
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
            'parent': pk+1000
        })
        self.assertEqual(response2.status_code, 400)
        self.assertIn('parent', response2.data)

    def test_with_user_who_cannot_see_parent(self):
        self.client.force_authenticate(user=self.with_permission)

        with_permission_group_ids = map(lambda g: g.id, self.with_permission.all_groups)

        group = AbakusGroup.objects.exclude(id__in=with_permission_group_ids).first()
        """
            create an article which has a different owner and a group which with_permission does not
            belong to. The user should then not be allowed to post a comment on this article
        """

        article = Article(
            text='hello world',
            author=self.without_permission
        )
        article.save()
        article.can_view_groups.add(group)

        content_type = ContentType.objects.get_for_model(Article)

        comment_target = '{0}.{1}-{2}'.format(
            content_type.app_label,
            content_type.model,
            article.id
        )

        response = self.client.post(_get_list_url(), {
            'comment_target': comment_target,
            'text': 'first comment'
        })

        self.assertEqual(response.status_code, 403)


class UpdateCommentsAPITestCase(APITestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml',
    ]

    def setUp(self):
        Comment.objects.create(
            created_by_id=4, text='first comment', content_object=Article.objects.get(id=1)
        )
        Comment.objects.create(
            created_by_id=3, text='second comment', content_object=Article.objects.get(id=2)
        )

        self.all_comments = Comment.objects.all()
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username='useradmin_test')
        self.comments_test_group = AbakusGroup.objects.get(name='CommentTest')
        self.comments_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(pk=self.with_permission.pk).first()
        self.test_comment = Comment.objects.first()

    modified_comment = {
        'text': 'whats up'
    }

    def successful_update(self, updater, update_object):
        self.client.force_authenticate(user=updater)
        response = self.client.patch(_get_detail_url(update_object.pk), self.modified_comment)
        comment = Comment.objects.get(pk=update_object.pk)
        self.assertEqual(response.status_code, 200)

        for key, value in self.modified_comment.items():
            self.assertEqual(getattr(comment, key), value)

    def test_self(self):
        self.successful_update(self.test_comment.created_by, self.test_comment)

    def test_with_useradmin(self):
        self.successful_update(self.with_permission, self.test_comment)

    def test_with_new_comment_target(self):
        comment_update = self.modified_comment.copy()

        content_type = ContentType.objects.get_for_model(Article)
        comment_target = '{0}.{1}-{2}'.format(
            content_type.app_label,
            content_type.model,
            Article.objects.last().pk
        )

        comment_update['comment_target'] = comment_target
        self.client.force_authenticate(user=self.with_permission)
        response = self.client.put(_get_detail_url(self.test_comment.pk), comment_update)
        comment = Comment.objects.get(pk=self.test_comment.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.content_object, self.test_comment.content_object)

    def test_other_with_normal_user(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.put(_get_detail_url(self.test_comment.pk), self.modified_comment)
        comment = Comment.objects.get(pk=self.test_comment.pk)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(comment, self.test_comment)


class DeleteUsersAPITestCase(APITestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_articles.yaml'
    ]

    def setUp(self):
        self.test_comment = Comment.objects.create(
            created_by_id=4, text='first comment', content_object=Article.objects.get(id=1)
        )
        self.test_comment_2 = Comment.objects.create(
            created_by_id=3, text='second comment', content_object=Article.objects.get(id=2)
        )

        self.all_comments = Comment.objects.all()
        self.all_users = User.objects.all()
        self.with_permission = self.all_users.get(username='useradmin_test')
        self.comments_test_group = AbakusGroup.objects.get(name='CommentTest')
        self.comments_test_group.add_user(self.with_permission)
        self.without_permission = self.all_users.exclude(pk=self.with_permission.pk).first()

    def successful_delete(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.delete(_get_detail_url(self.test_comment.pk))

        self.assertEqual(response.status_code, 204)
        self.assertRaises(Comment.DoesNotExist, Comment.objects.get, pk=self.test_comment.pk)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.delete(_get_detail_url(self.test_comment_2.pk))
        self.assertEqual(response.status_code, 403)

    def test_with_owner(self):
        self.successful_delete(self.test_comment.created_by)

    def test_with_useradmin(self):
        self.successful_delete(self.with_permission)
