from rest_framework import decorators, exceptions, mixins, permissions, renderers, viewsets
from rest_framework.response import Response

from .models import File
from .serializers import FileSerializer, FileUploadSerializer
from .utils import prepare_file_upload, validate_redirect_token
from .validators import KEY_REGEX_RAW


class FileViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer]
    queryset = File.objects.all()
    serializer_class = FileSerializer
    lookup_field = 'key'
    lookup_value_regex = KEY_REGEX_RAW

    def create(self, request, *args, **kwargs):
        """
        Upload new file. This method returns instructions to the client on how to upload the file.
        """
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        key = serializer.validated_data['key']
        url, fields = prepare_file_upload(key)

        return Response({
            'url': url,
            'fields': fields
        })

    @decorators.detail_route(
        methods=['GET'],
        permission_classes=[permissions.AllowAny],
        authentication_classes=[]
    )
    def upload_success(self, request, *args, **kwargs):
        """
        The client is redirected to this view when a upload succeeds. This view will inform the
        client with necessary data to change a file on a instance.
        """
        instance = self.get_object()
        token = request.GET.get('token')

        if validate_redirect_token(instance, token):
            instance.upload_done()

            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        raise exceptions.PermissionDenied('View requested with invalid token query param')
