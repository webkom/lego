from rest_framework_nested import routers

from lego.app.articles.views.articles import ArticlesViewSet
from lego.app.events.views.events import EventViewSet, PoolViewSet, RegistrationViewSet
from lego.app.flatpages.views import PageViewSet
from lego.users.views.abakus_groups import AbakusGroupViewSet
from lego.users.views.users import UsersViewSet

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'groups', AbakusGroupViewSet)
router.register(r'pages', PageViewSet)
router.register(r'articles', ArticlesViewSet)
router.register(r'events', EventViewSet)

events_router = routers.NestedSimpleRouter(router, r'events', lookup='event')
events_router.register(r'register', RegistrationViewSet, base_name='register')
events_router.register(r'pools', PoolViewSet)
pools_router = routers.NestedSimpleRouter(events_router, r'pools', lookup='pool')
pools_router.register(r'registrations', RegistrationViewSet)
