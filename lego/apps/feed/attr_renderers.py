from lego.apps.files.thumbor import generate_url


def render_user(user):
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'profile_picture': generate_url(user.profile_picture, height=100, width=100)
    }


def render_event(event):
    return {'id': event.id, 'title': event.title, 'event_type': event.event_type}


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
    return {'id': article.id, 'title': article.title}


def render_announcement(announcement):
    return {'id': announcement.id, 'message': announcement.message}


def render_gallery_picture(gallery_picture):
    return {
        'id': gallery_picture.id,
        'gallery': {
            'id': gallery_picture.gallery.id,
            'title': gallery_picture.gallery.title
        }
    }


def render_abakus_group(abakus_group):
    logo = None
    if abakus_group.logo_id:
        logo = generate_url(abakus_group.logo_id, height=100, width=100)

    return {
        'id': abakus_group.id,
        'name': abakus_group.name,
        'type': abakus_group.type,
        'logo': logo
    }


def render_registration(registration):
    pool = registration.pool
    return {
        'id': registration.id,
        'waiting_list': pool is None and registration.unregistration_date is None,
        'registered': not (pool is None and registration.unregistration_date),
    }


def render_restricted_mail(restrictedmail):
    return {'id': restrictedmail.id}
