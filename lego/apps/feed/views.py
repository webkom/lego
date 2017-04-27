from prometheus_client import Summary
from rest_framework import decorators, exceptions, permissions, status, viewsets
from rest_framework.response import Response

from lego.apps.feed.feeds.company_feed import CompanyFeed
from lego.apps.feed.feeds.group_feed import GroupFeed
from lego.apps.feed.feeds.notification_feed import NotificationFeed
from lego.apps.feed.feeds.personal_feed import PersonalFeed
from lego.apps.feed.feeds.user_feed import UserFeed
from lego.apps.users.models import User

from .attr_cache import AttrCache
from .serializers import AggregatedFeedSerializer, MarkSerializer, NotificationFeedSerializer

feed_attr_cache_timer = Summary('feed_attr_cache', 'Track feed AttrCache lookups')


class FeedViewSet(viewsets.GenericViewSet):
    """
    This is the baseviewset used to render most of our feeds.
    """

    feed_class = None
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = ()
    serializer_class = AggregatedFeedSerializer
    ordering = '-activity_id'

    @feed_attr_cache_timer.time()
    def attach_metadata(self, data):
        """
        Map over the feed here to attach more information to each element.
        """
        content_strings = set()

        for item in data:
            activities = item.get('activities')
            if activities:
                # Aggregated Activity
                for activity in activities:
                    target = activity.get('target')
                    object = activity.get('object')
                    actor = activity.get('actor')
                    content_strings.add(target) if target else None
                    content_strings.add(object) if object else None
                    content_strings.add(actor) if actor else None

        if content_strings:
            cache = AttrCache()
            lookup = cache.bulk_lookup(content_strings)

        for item in data:
            context = {}

            activities = item.get('activities')
            if activities:
                # Aggregated Activity
                for activity in activities:
                    target = activity.get('target')
                    object = activity.get('object')
                    actor = activity.get('actor')
                    if target in lookup.keys():
                        context[target] = lookup[target]
                    if object in lookup.keys():
                        context[object] = lookup[object]
                    if actor in lookup.keys():
                        context[actor] = lookup[actor]
            item['context'] = context

        return data

    def get_queryset(self):
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        try:
            feed_id = self.kwargs[lookup_url_kwarg]
        except (ValueError, TypeError):
            raise exceptions.ParseError
        return self.feed_class(feed_id)


class FeedRetrieveMixin:
    """
    Make the feed available as a retrieve method.
    """

    def retrieve(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self.attach_metadata(serializer.data))

        raise exceptions.APIException


class FeedListMixin:
    """
    Make the feed available as a list method.
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(self.attach_metadata(serializer.data))

        raise exceptions.APIException


class UserFeedViewSet(FeedViewSet, FeedRetrieveMixin):

    feed_class = UserFeed

    def get_queryset(self):
        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        try:
            feed_id = self.kwargs[lookup_url_kwarg]
        except (ValueError, TypeError):
            raise exceptions.ParseError

        try:
            feed_id = User.objects.values('id').get(username=feed_id)['id']
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            raise exceptions.NotFound

        return self.feed_class(feed_id)


class PersonalFeedViewSet(FeedViewSet, FeedListMixin):

    feed_class = PersonalFeed

    def get_queryset(self):
        return self.feed_class(self.request.user.pk)


class GroupFeedViewSet(FeedViewSet, FeedRetrieveMixin):

    feed_class = GroupFeed


class CompanyFeedViewSet(FeedViewSet, FeedRetrieveMixin):

    feed_class = CompanyFeed


class NotificationFeedViewSet(FeedViewSet, FeedListMixin):
    """
    This endpoint lists all notifications owned by the current user.
    Actions:
    * /mark_all
    * /{id}/mark
    * /notification_data
    """
    feed_class = NotificationFeed
    serializer_class = NotificationFeedSerializer

    def get_queryset(self):
        """
        We select the feed with request.user
        """
        return self.feed_class(self.request.user.pk)

    @decorators.list_route(
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=MarkSerializer,
        methods=['POST']
    )
    def mark_all(self, request):
        """
        This function marks all activities in a NotificationFeed as seen or/and red.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        feed = self.get_queryset()
        feed.mark_all(**data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.detail_route(
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=MarkSerializer,
        methods=['POST']
    )
    def mark(self, request, pk):
        """
        Mark a single notification as read or seen.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        feed = self.get_queryset()
        feed.mark_activity(pk, **data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.list_route(
        permission_classes=[permissions.IsAuthenticated],
        methods=['GET']
    )
    def notification_data(self, request):
        feed = self.get_queryset()
        return Response(feed.get_notification_data())
