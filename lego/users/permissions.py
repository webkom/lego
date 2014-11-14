# -*- coding: utf8 -*-
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly


class AbakusModelPermissions(DjangoModelPermissionsOrAnonReadOnly):
    perms_map = {
        'GET': [],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': [],
        'PATCH': [],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }
