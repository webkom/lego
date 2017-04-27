from django_thumbor import generate_url


def render_user(user):
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_picture': generate_url(user.profile_picture, height=100, width=100)
    }


def render_event(event):
    return {
        'id': event.id,
        'title': event.title,
        'event_type': event.event_type
    }


def render_meeting_invitation(meeting_invitation):
    return {
        'id': meeting_invitation.id,
        'meeting': {
            'id': meeting_invitation.meeting.id,
            'title': meeting_invitation.meeting.title,
            'start_time': meeting_invitation.meeting.start_time,
            'location': meeting_invitation.meeting.location
        }
    }


def render_article(article):
    return {
        'id': article.id,
        'title': article.title
    }
