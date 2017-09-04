from datetime import timedelta

from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
from django_ical import feedgenerator
from rest_framework import decorators, permissions, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings

from lego.apps.events.models import Event
from lego.apps.ical import constants
from lego.apps.ical.authentication import ICalTokenAuthentication
from lego.apps.meetings.models import Meeting
from lego.apps.permissions.utils import get_permission_handler

from .models import ICalToken
from .serializers import ICalTokenSerializer


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

                'token': ICalTokenSerializer(token).data
            }
        }
        return Response(data=data)

    @decorators.list_route(methods=['GET'])
    def personal(self, request):
        """Personal ical route."""
        feed = feedgenerator.ICal20Feed(
            title=constants.ICAL_PERSONAL_TITLE,
            link=request.get_full_path,
            description=constants.ICAL_PERSONAL_DESC,
            language='nb',
        )

        permission_handler = get_permission_handler(Event)
        following_events = permission_handler.filter_queryset(
            request.user,
            Event.objects.filter(
                followers__follower_id=request.user.id,
                end_time__gt=timezone.now() - timedelta(
                    days=constants.ICAL_HISTORY_BACKWARDS_IN_DAYS
                )
            ).all()
        )

        permission_handler = get_permission_handler(Meeting)
        meetings = permission_handler.filter_queryset(
            request.user,
            Meeting.objects.filter(
                end_time__gt=timezone.now() - timedelta(
                    days=constants.ICAL_HISTORY_BACKWARDS_IN_DAYS
                )
            )
        )

        desc_event = loader.get_template('ical/event_description.txt')
        for event in following_events:
            context = {
                'description': event.description,
                'url': event.get_absolute_url()
            }
            feed.add_item(
                title=event.title,
                unique_id=f'event-{event.id}@abakus.no',
                link=event.get_absolute_url(),
                description=desc_event.render(context),
                start_datetime=event.start_time,
                end_datetime=event.end_time,
                location=event.location
            )

        desc = loader.get_template('ical/meeting_description.txt')
        for meeting in meetings:
            context = {
                'title': meeting.title,
                'report': meeting.report,
                'reportAuthor':
                meeting.report_author.username if meeting.report_author else 'Ikke valgt',
                'url': meeting.get_absolute_url()
            }
            feed.add_item(
                title=meeting.title,
                link=meeting.get_absolute_url(),
                description=desc.render(context),
                location=meeting.location,
                unique_id=f'meeting-{meeting.id}@abakus.no',
                start_datetime=meeting.start_time,
                end_datetime=meeting.end_time
            )

        response = HttpResponse()
        feed.write(response, 'utf-8')
        return response

    @decorators.list_route(methods=['GET'])
    def registrations(self, request):
        """Registration ical route."""
        feed = feedgenerator.ICal20Feed(
            title=constants.ICAL_REGISTRATIONS_TILE,
            link=request.get_full_path,
            description=constants.ICAL_REGISTRATIONS_DESC,
            language='nb',
        )

        permission_handler = get_permission_handler(Event)
        events = permission_handler.filter_queryset(
            request.user,
            Event.objects.all().filter(
                end_time__gt=timezone.now()
            )
        )

        desc = loader.get_template('ical/event_description.txt')
        for event in events:
            reg_time = event.get_earliest_registration_time(request.user)
            if not reg_time:
                continue

            context = {
                'description': event.description,
                'price': event.get_price(request.user),
                'url': event.get_absolute_url()
            }

            feed.add_item(
                title=f'Reg: {event.title}',
                link=event.get_absolute_url(),
                description=desc.render(context),
                unique_id=f'event-{event.id}@abakus.no',
                start_datetime=reg_time,
                location=event.location,
                end_datetime=reg_time + timedelta(
                    minutes=constants.ICAL_REGISTRATION_EVENT_LENGTH_IN_MINUTES
                )
            )
        response = HttpResponse()
        feed.write(response, 'utf-8')

        return response

    @decorators.list_route(methods=['GET'])
    def events(self, request):
        """Event ical route."""
        feed = feedgenerator.ICal20Feed(
            title=constants.ICAL_EVENTS_TITLE,
            link=request.get_full_path,
            description=constants.ICAL_EVENTS_DESC,
            language='nb',
        )

        permission_handler = get_permission_handler(Event)
        events = permission_handler.filter_queryset(
            request.user,
            Event.objects.all().filter(
                end_time__gt=timezone.now() - timedelta(
                    days=constants.ICAL_HISTORY_BACKWARDS_IN_DAYS
                )
            )
        )

        desc = loader.get_template('ical/event_description.txt')
        for event in events:
            context = {
                'description': event.description,
                'price': event.get_price(request.user),
                'url': event.get_absolute_url()
            }
            feed.add_item(
                title=event.title,
                link=event.get_absolute_url(),
                description=desc.render(context),
                unique_id=f'event-{event.id}@abakus.no',
                location=event.location,
                start_datetime=event.start_time,
                end_datetime=event.end_time
            )
        response = HttpResponse()
        feed.write(response, 'utf-8')
        return response
