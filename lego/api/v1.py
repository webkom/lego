from rest_framework import routers

from lego.app.articles.views.articles import ArticlesViewSet
from lego.app.comments.views.comments import CommentViewSet
from lego.app.events.views import EventViewSet, PoolViewSet, RegistrationViewSet
from lego.app.feed.views import NotificationFeedViewSet
from lego.app.flatpages.views import PageViewSet
from lego.users.views.abakus_groups import AbakusGroupViewSet
from lego.users.views.users import UsersViewSet

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'groups', AbakusGroupViewSet)
router.register(r'pages', PageViewSet)
router.register(r'articles', ArticlesViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'events', EventViewSet)
router.register(r'events/(?P<event_pk>[^/]+)/pools', PoolViewSet)
router.register(r'events/(?P<event_pk>[^/]+)/register',
                RegistrationViewSet, base_name='register')
router.register(r'notifications', NotificationFeedViewSet, base_name='feed-notifications')
