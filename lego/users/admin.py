# -*- coding: utf8 -*-

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from lego.users.models import User


class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
