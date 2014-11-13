# -*- coding: utf8 -*-
from rest_framework import routers

from lego.users.views.users import UsersViewSet
from lego.app.flatpages.api import PageViewSet

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'pages', PageViewSet)
