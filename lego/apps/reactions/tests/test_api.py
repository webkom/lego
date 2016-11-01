from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase


from lego.apps.reactions.models import ReactionType, Reaction
from lego.apps.articles.models import Article
from lego.apps.users.models import AbakusGroup, User


def _get_list_url():
    return reverse('api:v1:reaction-list')


def _get_detail_url(pk):
    return reverse('api:v1:reaction-detail', kwargs={'pk': pk})


class CreateReactionsAPITestCase(APITestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_reaction_types.yaml', 'test_articles.yaml'
    ]

    def get_test_data(self, article_id):
        content_type = ContentType.objects.get_for_model(Article)
        return {
            'type': ReactionType.objects.first().pk,
            'target': '{0}.{1}-{2}'.format(
                content_type.app_label,
                content_type.model,
                article_id
            )
        }

    def setUp(self):
        self.article = Article.objects.get(pk=1)
        self.test_data = self.get_test_data(self.article.pk)
        group = AbakusGroup.objects.get(name="ReactionTest")
        self.article.can_view_groups.add(group)

        self.authorized_user = User.objects.get(pk=1)
        group.add_user(self.authorized_user)

        self.unauthorized_user = User.objects.get(pk=2)

    def test_unauthenticated_create(self):
        response = self.client.post(_get_list_url(), self.test_data)
        self.assertEqual(response.status_code, 401)

    def test_unauthorized_create(self):
        self.client.force_authenticate(self.unauthorized_user)
        response = self.client.post(_get_list_url(), self.test_data)
        self.assertEqual(response.status_code, 403)

    def test_authorized_create(self):
        self.client.force_authenticate(self.authorized_user)
        response = self.client.post(_get_list_url(), self.test_data)
        self.assertEqual(response.status_code, 201)

    def test_reacting_on_nonexistent_object(self):
        test_data = self.get_test_data(10000)
        self.client.force_authenticate(self.authorized_user)
        response = self.client.post(_get_list_url(), test_data)
        self.assertEqual(response.status_code, 400)


    def test_invalid_reaction_type(self):
        test_data = {
            **self.test_data,
            'type': 'xxxyzb'
        }
        self.client.force_authenticate(self.authorized_user)
        response = self.client.post(_get_list_url(), test_data)
        self.assertEqual(response.status_code, 400)



class DeleteReactionsAPITestCase(APITestCase):
    fixtures = [
        'test_abakus_groups.yaml', 'test_users.yaml', 'test_reaction_types.yaml',
        'test_articles.yaml'
    ]

    def setUp(self):
        self.test_reaction = Reaction.objects.create(
            content_object=Article.objects.get(id=1), type=ReactionType.objects.first()
        )
        self.test_reaction.created_by = User.objects.get(pk=4)
        self.test_reaction.save()

        self.with_permission = User.objects.get(username='useradmin_test')
        group = AbakusGroup.objects.get(name='ReactionAdminTest')
        group.add_user(self.with_permission)
        self.without_permission = User.objects.exclude(pk=self.with_permission.pk).first()

    def successful_delete(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.delete(_get_detail_url(self.test_reaction.pk))
        self.assertEqual(response.status_code, 204)
        self.assertRaises(Reaction.DoesNotExist, Reaction.objects.get, pk=self.test_reaction.pk)

    def test_with_normal_user(self):
        self.client.force_authenticate(user=self.without_permission)
        response = self.client.delete(_get_detail_url(self.test_reaction.pk))
        self.assertEqual(response.status_code, 403)

    def test_with_owner(self):
        self.successful_delete(self.test_reaction.created_by)

    def test_with_useradmin(self):
        self.successful_delete(self.with_permission)
