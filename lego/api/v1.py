from lego.app.articles.views.articles import ArticlesViewSet
from lego.app.events.views.events import EventViewSet, PoolViewSet, RegistrationViewSet
from lego.app.flatpages.views import PageViewSet
from lego.users.views.abakus_groups import AbakusGroupViewSet
from lego.users.views.users import UsersViewSet

from .router import NestedDefaultRouter

router = NestedDefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'groups', AbakusGroupViewSet)
router.register(r'pages', PageViewSet)
router.register(r'articles', ArticlesViewSet)

events_router = router.register(r'events', EventViewSet, base_name='event')
events_router.register(
    r'register',
    RegistrationViewSet,
    base_name='event-register',
    parents_query_lookups=['event']
)
events_pools_registration_router = events_router.register(
    r'pools',
    PoolViewSet,
    base_name='event-pool',
    parents_query_lookups=['event']
)
events_pools_registration_router.register(
    r'register',
    RegistrationViewSet,
    base_name='event-pool-register',
    parents_query_lookups=['event', 'pool']
)
