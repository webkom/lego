from lego.apps.articles.views.articles import ArticlesViewSet
from lego.apps.comments.views.comments import CommentViewSet
from lego.apps.events.views import EventViewSet, PoolViewSet, RegistrationViewSet
from lego.apps.feed.views import NotificationFeedViewSet
from lego.apps.flatpages.views import PageViewSet
from lego.apps.oauth.views import AccessTokenViewSet, ApplicationViewSet
from lego.apps.quotes.views import QuoteViewSet
from lego.apps.search.views import AutocompleteViewSet, SearchViewSet
from lego.apps.users.views.abakus_groups import AbakusGroupViewSet
from lego.apps.users.views.users import UsersViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'groups', AbakusGroupViewSet)
router.register(r'pages', PageViewSet)
router.register(r'articles', ArticlesViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'notifications', NotificationFeedViewSet, base_name='feed-notifications')
router.register(r'events', EventViewSet)
router.register(r'events/(?P<event_pk>[^/]+)/pools', PoolViewSet)
router.register(r'events/(?P<event_pk>[^/]+)/registrations',
                RegistrationViewSet, base_name='registrations')
router.register(r'oauth2/applications', ApplicationViewSet)
router.register(r'oauth2/access-tokens', AccessTokenViewSet)
router.register(r'search/search', SearchViewSet, base_name='search')
router.register(r'search/autocomplete', AutocompleteViewSet, base_name='autocomplete')
router.register(r'quotes', QuoteViewSet)
