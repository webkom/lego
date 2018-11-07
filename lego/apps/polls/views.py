from rest_framework import viewsets, decorators

from lego.apps.permissions.api.views import AllowedPermissionsMixin
from lego.apps.polls.models import Poll
from lego.apps.polls.serializers import (PollSerializer, PollCreateSerializer,
                                         PollUpdateSerializer,
                                         DetailedPollSerializer)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class PollViewSet(AllowedPermissionsMixin, viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    ordering = '-created_at'

    def get_serializer_class(self):
        if self.action == 'create':
            return PollCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PollUpdateSerializer
        elif self.action == 'retrieve':
            return DetailedPollSerializer
        return PollSerializer

    @decorators.detail_route(
        methods=['POST'], permission_classes=[IsAuthenticated])
    def vote(self, request, *args, **kwargs):
        poll = self.get_object()
        poll.vote(request.user, request.data['option_id'])
        serializer = self.get_serializer_class()(
            poll, context={
                'request': request
            })
        return Response(serializer.data)
