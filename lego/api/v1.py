# -*- coding: utf8 -*-
from lego.users.views.abakus_groups import AbakusGroupViewSet
from rest_framework import routers

from lego.users.views.users import UsersViewSet
from lego.app.flatpages.views import PageViewSet

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'groups', AbakusGroupViewSet)
router.register(r'pages', PageViewSet)
