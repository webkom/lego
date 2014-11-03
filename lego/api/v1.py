# -*- coding: utf8 -*-
from lego.users.views.users import UsersViewSet
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'users', UsersViewSet)
