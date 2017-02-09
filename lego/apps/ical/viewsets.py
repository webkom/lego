from rest_framework import decorators, viewsets
from django.http import HttpResponse
from rest_framework.response import Response

from lego.apps.events.models import Event
from lego.apps.meetings.models import Meeting


from django_ical import feedgenerator
from datetime import datetime, timedelta


from .permissions import ICalTokenPermission
from .models import ICalToken
from .serializers import ICalTokenSerializer

from rest_framework.permissions import IsAuthenticated


class ICalTokenViewset(viewsets.ViewSet):
    """
    API Endpoint to get a token for ical-urls.

    To regenerate go to [regenerate](regenerate/).
    """

    permission_classes = (IsAuthenticated, )

    @decorators.list_route(methods=['GET'])
    def get(self, request, *args, **kwargs):
        """Get ICalToken."""
        token = ICalToken.objects.get_or_create(user=request.user)[0]
        serializer = ICalTokenSerializer(token)
        return Response(serializer.data)

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

    permission_classes = (ICalTokenPermission,)

    def list(self, request):
        """List all the different icals."""
        path = request.get_full_path()
        data = {
            'calendars': [
                {
                    'name': 'events',
                    'description': 'All events you can see.',
                    'path': f'{path}events/'
                },
                {
                    'name': 'meetings',
                    'description': 'All your meetings.',
                    'path': f'{path}meetings/'
                },
                {
                    'name': 'favorites',
                    'description': 'All your favorite events.',
                    'path': f'{path}events/'
                },
                {
                    'name': 'registration',
                    'description': 'All event registration times',
                    'path': f'{path}registrations/'
                },
            ]
        }
        return Response(data=data)

    def addEvents(feed, events):
        """Add events to the given feed."""
        pass

    def addMeetings(self, feed, meetings):
        """Add meetings to the given feed."""
        for meeting in meetings:
            feed.add_item(
                title=meeting.title,
                link=meeting.get_absolute_url(),
                description=f'{meeting.report}\n\n{meeting.get_absolute_url()}',
                start_datetime=meeting.start_time,
                end_datetime=meeting.end_time
            )

    @decorators.list_route(methods=['GET'])
    def meetings(self, request):
        """Meeting ical route."""
        feed = feedgenerator.ICal20Feed(
            title=u"ICalendar for " + str(request.token_user),
            link=u"https://api.abakus.no/api/v1/calendar/ical/events.ics",
            description=u"List of events from Abakus.no",
            language=u"nb",
        )

        self.addMeetings(feed, Meeting.objects.all())

        response = HttpResponse()
        feed.write(response, 'utf-8')
        return response

    @decorators.list_route(methods=['GET'])
    def registrations(self, request):
        """Registrations ical route."""
        feed = feedgenerator.ICal20Feed(
            title=u"ICalendar for " + str(request.token_user),
            link=request.get_full_path(),
            description=u"List of registration time for events from Abakus.no",
            language=u"nb",
        )

        events = (Event.objects
                  .all()
                  .order_by('-start_time')
                  # Filter removed for testing
                  # .filter(end_time__gt=datetime.today())
                  )

        for event in events:
            reg_time = event.get_earliest_registration_time(request.token_user)
            if not reg_time:
                continue

            feed.add_item(
                title=f'Reg: {event.title}',
                link=event.get_absolute_url(),
                description=event.description,
                start_datetime=reg_time,
                end_datetime=reg_time + timedelta(minutes=15)
            )
        response = HttpResponse()
        feed.write(response, 'utf-8')

        return response

    @decorators.list_route(methods=['GET'])
    def events(self, request):
        """Event ical route."""
        feed = feedgenerator.ICal20Feed(
            title=u"ICalendar for " + str(request.token_user),
            link=u"https://api.abakus.no/api/v1/calendar/ical/events.ics",
            description=u"List of events from Abakus.no",
            language=u"nb",
        )

        events = (Event.objects
                  .all()
                  .order_by('-start_time')
                  .filter(end_time__gt=datetime.today() - timedelta(days=7)))
        for event in events:
            feed.add_item(
                title=event.title,
                link=event.get_absolute_url(),
                description=event.description,
                start_datetime=event.start_time,
                end_datetime=event.end_time
            )
        response = HttpResponse()
        feed.write(response, 'utf-8')
        return response

    @decorators.list_route(methods=['GET'])
    def favorites(self, request):
        """Event favorites ical route."""
        return self.events(request)
