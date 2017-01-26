from rest_framework import decorators, status, viewsets
from rest_framework.response import Response

from lego.apps.followers.models import Follower, FollowEvent, FollowUser
from lego.apps.followers.serializers import (FollowerSerializer, FollowEventSerializer,
                                             FollowUserSerializer)
from lego.utils.content_types import VALIDATION_EXCEPTIONS, string_to_instance


class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer

    def create(self, request, *args, **kwargs):
        follow_target = self.get_follow_target(request)

        if follow_target:
            if isinstance(follow_target, 'events.Event'):
                serializer = FollowEventSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user_id = request.user.id

                follow = FollowEvent.objects.create(follower_id=user_id,
                                                    follow_target=follow_target)
                follower_serializer = FollowEventSerializer(follow)

                return Response(data=follower_serializer.data, status=status.HTTP_201_CREATED)

            elif isinstance(follow_target, 'users.User'):
                serializer = FollowUserSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user_id = request.user.id

                follow = FollowUser.objects.create(follower_id=user_id,
                                                   follow_target=follow_target)
                follower_serializer = FollowUserSerializer(follow)

                return Response(data=follower_serializer.data, status=status.HTTP_201_CREATED)

    @decorators.list_route(methods=['GET'])
    def get_event_followers(self, request):
        follow_target = self.get_follow_target(self, request)

        if follow_target & isinstance(follow_target, 'events.Event'):
            followers = FollowEvent.objects.filter(follow_target=follow_target)
            response_data = []

            for follower in followers:
                serializer = FollowerSerializer(follower)
                response_data.append(serializer.data)

            return Response(data=response_data, status=status.HTTP_200_OK)

    @decorators.list_route(methods=['GET'])
    def get_user_followers(self, request):
        follow_target = self.get_follow_target(self, request)

        if follow_target & isinstance(follow_target, 'users.User'):
            followers = FollowUser.objects.filter(follow_target=follow_target)
            response_data = []

            for follower in followers:
                serializer = FollowerSerializer(follower)
                response_data.append(serializer.data)

            return Response(data=response_data, status=status.HTTP_200_OK)

    @decorators.list_route(methods=['GET'])
    def get_following(self, request):
        user = None

        try:
            if request.data.get('follower') is not None:
                user = string_to_instance(request.data.get('follower'))

        except VALIDATION_EXCEPTIONS:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        following = Follower.objects.filter(follower=user)
        response_data = []

        for item in following:
            if isinstance(item, FollowEvent):
                serializer = FollowEventSerializer(item)
                response_data.append(serializer.data)
            elif isinstance(item, FollowUser):
                serializer = FollowUserSerializer(item)
                response_data.append(serializer.data)

        return Response(data=response_data, status=status.HTTP_200_OK)

    def get_follow_target(self, request):
        try:
            if request.data.get('follow_target') is not None:
                return string_to_instance(request.data.get('follow_target'))

        except VALIDATION_EXCEPTIONS:
            return Response(status=status.HTTP_400_BAD_REQUEST)
