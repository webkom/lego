from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpResponse
from django.template import loader

from django_ical import feedgenerator

from lego.apps.ical import constants


def add_events_to_ical_feed(
    feed, events, price=None, title=None, ical_starttime=None, ical_endtime=None
):
    for event in events:
        add_event_to_ical_feed(feed, event, price, title, ical_starttime, ical_endtime)


def add_meetings_to_ical_feed(feed, meetings, user):
    for meeting in meetings:
        add_meeting_to_ical_feed(feed, meeting, user)


def add_event_to_ical_feed(
    feed, event, price=None, title=None, ical_starttime=None, ical_endtime=None
):
    desc_context = {"description": event.description, "url": event.get_absolute_url()}
    if price is not None:
        desc_context["price"] = int(price / 100)  # Price is in øre NOK, show as NOK

    desc_template = loader.get_template("ical/event_description.txt")
    feed.add_item(
        title=event.title if title is None else title,
        unique_id=f"event-{event.id}@abakus.no",
        link=event.get_absolute_url(),
        description=desc_template.render(desc_context),
        start_datetime=event.start_time if ical_starttime is None else ical_starttime,
        end_datetime=event.end_time if ical_endtime is None else ical_endtime,
        location=event.location,
    )


def add_meeting_to_ical_feed(feed, meeting, user):
    desc_context = {
        "title": meeting.title,
        "report": meeting.report,
        "description": meeting.description,
        "reportAuthor": (
            meeting.report_author.full_name if meeting.report_author else "Ikke valgt"
        ),
        "url": meeting.get_absolute_url(),
    }
    desc_template = loader.get_template("ical/meeting_description.txt")

    is_participating = True
    if hasattr(meeting, "user_participating"):
        is_participating = meeting.user_participating
    else:
        from lego.apps.meetings import constants as meeting_constants

        not_participating = meeting.invitations.filter(
            user=user,
            status__in=[meeting_constants.NOT_ATTENDING, meeting_constants.NO_ANSWER],
        ).exists()
        is_participating = not not_participating

    feed.add_item(
        title=meeting.title,
        unique_id=f"meeting-{meeting.id}@abakus.no",
        link=meeting.get_absolute_url(),
        description=desc_template.render(desc_context),
        start_datetime=meeting.start_time,
        end_datetime=meeting.end_time,
        location=meeting.location,
        transparency="OPAQUE" if is_participating else "TRANSPARENT",
    )


def generate_ical_feed(request, calendar_type):
    return feedgenerator.ICal20Feed(
        title=get_calendar_name(calendar_type),
        link=request.get_full_path(),
        description=get_calendar_description(calendar_type),
        language="nb",
        method="PUBLISH",
        product_id="-//Abakus//Abakus.no//EN",
    )


def render_ical_response(feed, calendar_type):
    response = HttpResponse(content_type="text/calendar")
    feed.write(response, "utf-8")
    response["Content-Disposition"] = f'attachment; filename="{calendar_type}.ics"'
    response["Filename"] = f"{calendar_type}.ics"
    return response


def get_frontend_domain():
    return urlsplit(settings.FRONTEND_URL).netloc


def get_calendar_name(calendar_type):
    return f"{get_frontend_domain()} - {constants.TITLES[calendar_type]}"


def get_calendar_description(calendar_type):
    return f"{constants.DESCRIPTIONS[calendar_type]}"
