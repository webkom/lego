# -*- coding: utf8 -*-
from django.contrib import admin

from .models import UserMapping, GroupMapping, RawMapping, RawMappingElement

admin.site.register(UserMapping)
admin.site.register(GroupMapping)
admin.site.register(RawMapping)
admin.site.register(RawMappingElement)
