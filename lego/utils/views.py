from rest_framework import viewsets

from lego.apps.permissions.backends import AbakusViewSetPermission


class AbakusModelViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        response.data['permissions'] = AbakusViewSetPermission.get_permissions(
            self,
            # We don't need the actual object here, just the model to get the name and label
            self.get_serializer_class().Meta.model,
            request.user
        )
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, args, kwargs)
        response.data['permissions'] = AbakusViewSetPermission.get_permissions(
            self,
            # FIXME: A better way to do this?
            self.get_serializer_class().Meta.model.objects.get(pk=self.kwargs['pk']),
            request.user
        )
        return response
