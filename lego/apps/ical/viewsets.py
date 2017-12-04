from datetime import timedelta

from django.utils import timezone
from rest_framework import decorators, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings

from lego.apps.events.models import Event
from lego.apps.ical import constants, utils
from lego.apps.ical.authentication import ICalTokenAuthentication
from lego.apps.ical.models import ICalToken
from lego.apps.ical.serializers import ICalTokenSerializer
from lego.apps.meetings.models import Meeting
from lego.apps.permissions.utils import get_permission_handler


class ICalTokenViewset(viewsets.ViewSet):
    """
    API Endpoint to get a token for ical-urls.

    To regenerate go to [regenerate](regenerate/).
    """

    permission_classes = (IsAuthenticated, )

    @decorators.list_route(methods=['PATCH'])
    def regenerate(self, request, *args, **kwargs):
        """Regenerate ICalToken."""
        token, created = ICalToken.objects.get_or_create(user=request.user)
        if not created:
            token.regenerate()
        serializer = ICalTokenSerializer(token)
        return Response(serializer.data)

    def list(self, request):
        """Get ICalToken."""
        token = ICalToken.objects.get_or_create(user=request.user)[0]
        serializer = ICalTokenSerializer(token)
        return Response(serializer.data)


class ICalViewset(viewsets.ViewSet):
    """
    API Endpoint to get ICalendar files for different kinds of events and meetings.

    usage: [events/?token=yourtoken](events/?token=yourtoken)
    """

    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES + [ICalTokenAuthentication]

    def list(self, request):
        """List all the different icals."""
        token = ICalToken.objects.get_or_create(user=request.user)[0]
        path = request.get_full_path()
        data = {
            'result': {
                'calendars': [
                    {
                        'name': 'events',
                        'description': 'Calendar with all events on Abakus.no.',
                        'path': f'{path}events/'
                    },
                    {
                        'name': 'personal',
                        'description': 'Calendar with your favorite events & meetings.',
                        'path': f'{path}personal/'
                    },
                    {
                        'name': 'registration',
                        'description': 'Calendar with all event registration times.',
                        'path': f'{path}registrations/'
                    },
                ],
                'token':
                ICalTokenSerializer(token).data
            }
        }
        return Response(data=data)

    @decorators.list_route(methods=['GET'])
    def personal(self, request):
        """Personal ical route."""
        calendar_type = constants.TYPE_PERSONAL
        feed = utils.generate_ical_feed(request, calendar_type)

        following_events = Event.objects.filter(
            followers__follower_id=request.user.id,
            end_time__gt=timezone.now() - timedelta(days=constants.HISTORY_BACKWARDS_IN_DAYS)
        ).all()

        permission_handler = get_permission_handler(Meeting)
        meetings = permission_handler.filter_queryset(
            request.user,
            Meeting.objects.filter(
                end_time__gt=timezone.now() - timedelta(days=constants.HISTORY_BACKWARDS_IN_DAYS)
            )
        )

        utils.add_events_to_ical_feed(feed, following_events)
        utils.add_meetings_to_ical_feed(feed, meetings)

        return utils.render_ical_response(feed, calendar_type)

    @decorators.list_route(methods=['GET'])
    def registrations(self, request):
        """Registration ical route."""
        calendar_type = constants.TYPE_REGISTRATIONS
        feed = utils.generate_ical_feed(request, calendar_type)

        events = Event.objects.all().filter(end_time__gt=timezone.now())

        for event in events:
            reg_time = event.get_earliest_registration_time(request.user)
            if not reg_time:  # User cannot register
                continue

            ical_starttime = reg_time
            ical_endtime = ical_starttime + timedelta(
                minutes=constants.REGISTRATION_EVENT_LENGTH_IN_MINUTES
            )
            price = event.get_price(request.user) if event.is_priced else None
            title = f'Reg: {event.title}'

            utils.add_event_to_ical_feed(
                feed, event, price=price, title=title, ical_starttime=ical_starttime,
                ical_endtime=ical_endtime
            )
        return utils.render_ical_response(feed, calendar_type)

    @decorators.list_route(methods=['GET'])
    def events(self, request):
        """Event ical route."""
        calendar_type = constants.TYPE_EVENTS
        feed = utils.generate_ical_feed(request, calendar_type)

        events = Event.objects.all().filter(
            end_time__gt=timezone.now() - timedelta(days=constants.HISTORY_BACKWARDS_IN_DAYS)
        )

        utils.add_events_to_ical_feed(feed, events)

        return utils.render_ical_response(feed, calendar_type)
