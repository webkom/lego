# -*- coding: utf8 -*-
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.users.models import AbakusGroup, Membership
from lego.users.serializers import AbakusGroupSerializer, PublicAbakusGroupSerializer
from lego.users.filters import AbakusGroupFilterBackend
from lego.permissions.model_permissions import PostDeleteModelPermissions


class AbakusGroupViewSet(viewsets.ModelViewSet):
    queryset = AbakusGroup.objects.all()
    serializer_class = AbakusGroupSerializer
    permission_classes = (IsAuthenticated, PostDeleteModelPermissions)
    filter_backend = AbakusGroupFilterBackend

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = AbakusGroup.objects.all()
        group = get_object_or_404(queryset, pk=pk)

        if (not request.user.has_perm('users.retrieve_abakusgroup')
                and group not in request.user.all_groups):
            serializer = PublicAbakusGroupSerializer(group)
        else:
            serializer = AbakusGroupSerializer(group)

        return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        try:
            Membership.objects.get(group=pk, role=Membership.LEADER)
        except Membership.DoesNotExist:
            if not request.user.has_perm('users.change_abakusgroup'):
                raise PermissionDenied()

        return super(AbakusGroupViewSet, self).update(request, *args, **kwargs)
