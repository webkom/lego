from rest_framework import routers

from lego.app.articles.views.articles import ArticlesViewSet
from lego.app.comments.views.comments import CommentViewSet
from lego.app.events.views.events import EventViewSet
from lego.app.flatpages.views import PageViewSet
from lego.users.views.abakus_groups import AbakusGroupViewSet
from lego.users.views.users import UsersViewSet

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'groups', AbakusGroupViewSet)
router.register(r'pages', PageViewSet)
router.register(r'articles', ArticlesViewSet)
router.register(r'events', EventViewSet)
router.register(r'comments', CommentViewSet)
