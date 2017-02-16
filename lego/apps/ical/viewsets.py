from datetime import timedelta

from django.http import HttpResponse
from django.template import Context, loader
from django.utils import timezone
from django_ical import feedgenerator
from rest_framework import decorators, filters, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.apps.events.models import Event
from lego.apps.ical import constants
from lego.apps.meetings import filters as meeting_filters
from lego.apps.meetings.models import Meeting
from lego.apps.permissions.filters import AbakusObjectPermissionFilter, filter_queryset

from .models import ICalToken
from .permissions import ICalTokenPermission
from .serializers import ICalTokenSerializer


class ICalTokenViewset(viewsets.ViewSet):
    """
    API Endpoint to get a token for ical-urls.

    To regenerate go to [regenerate](regenerate/).
    """

    permission_classes = (IsAuthenticated, )

    @decorators.list_route(methods=['GET', 'POST'])
    def regenerate(self, request, *args, **kwargs):
        """Regenerate ICalToken."""
        ICalToken.objects.get(user=request.user).delete()
        token = ICalToken.objects.create(user=request.user)
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

    To get a token, see [token](../token/).

    usage: [events/?token=yourtoken](events/?token=yourtoken)
    """

    filter_backends = (AbakusObjectPermissionFilter, filters.DjangoFilterBackend,)
    queryset = Event.objects.all()

    permission_classes = (ICalTokenPermission, )

    def list(self, request):
        """List all the different icals."""
        token = ICalToken.objects.get_or_create(user=request.token_user)[0]
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
            title=u"ICalendar for user: " + str(request.token_user),
            link=request.get_full_path,
            description=u"List of favorite events and meetings from Abakus.no",
            language=u"nb",
        )
        # TODO FIXME add favorite events

        meetings = meeting_filters.filter_queryset(
            request.token_user,
            Meeting.objects.filter(
                end_time__gt=timezone.now() - timedelta(
                    days=constants.ICAL_HISTORY_BACKWARDS_IN_DAYS
                )
            )
        )
        desc = loader.get_template("ical/meeting_description.txt")
        for meeting in meetings:
            context = Context({
                "title": meeting.title,
                "report": meeting.report,
                "reportAuthor":
                meeting.report_author.username if meeting.report_author else 'Ikke valgt',
                "url": meeting.get_absolute_url()
            })
            feed.add_item(
                title=meeting.title,
                link=meeting.get_absolute_url(),
                description=desc.render(context),
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
            title=u"ICalendar for " + str(request.token_user),
            link=request.get_full_path,
            description=u"List of registration time for events from Abakus.no",
            language=u"nb",
        )

        events = filter_queryset(
            request.user,
            Event.objects.all().filter(
                end_time__gt=timezone.now()
            )
        )

        desc = loader.get_template("ical/event_description.txt")
        for event in events:
            reg_time = event.get_earliest_registration_time(request.token_user)
            if not reg_time:
                continue

            context = Context({
                "description": event.description,
                "price": event.get_price(request.token_user),
                "url": event.get_absolute_url()
            })

            feed.add_item(
                title=f'Reg: {event.title}',
                link=event.get_absolute_url(),
                description=desc.render(context),
                start_datetime=reg_time,
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
            title=u"ICalendar for " + str(request.token_user),
            link=request.get_full_path,
            description=u"List of events from Abakus.no",
            language=u"nb",
        )

        events = filter_queryset(
            request.user,
            Event.objects.all().filter(
                end_time__gt=timezone.now() - timedelta(
                    days=constants.ICAL_HISTORY_BACKWARDS_IN_DAYS
                )
            )
        )

        desc = loader.get_template("ical/event_description.txt")
        for event in events:
            context = Context({
                "description": event.description,
                "price": event.get_price(request.token_user),
                "url": event.get_absolute_url()
            })
            feed.add_item(
                title=event.title,
                link=event.get_absolute_url(),
                description=desc.render(context),
                start_datetime=event.start_time,
                end_datetime=event.end_time
            )
        response = HttpResponse()
        feed.write(response, 'utf-8')
        return response
