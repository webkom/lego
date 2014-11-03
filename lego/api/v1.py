# -*- coding: utf8 -*-
from rest_framework import routers

from lego.users.views.users import UsersViewSet


router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
