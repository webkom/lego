from django.test import TestCase

from lego.apps.followers.models import FollowUser
from lego.apps.users.models import User


class FollowerTestCase(TestCase):

    def test_followuser_fields(self):
        follower = User(username=1, first_name=1, last_name=1, email=1)
        follower.save()
        followed = User(username=2, first_name=2, last_name=2, email=2)
        followed.save()

        follow = FollowUser.objects.create(follower=follower, followed_user=followed)

        self.assertEqual(follow.follower, follower)
        self.assertEqual(follow.followed_user, followed)
        print(follower.following.all())
        print(followed.followers.all())
        self.assertEqual(followed.followers.first().follower, follower)
        self.assertEqual(follower.following.first().followed_user, followed)
