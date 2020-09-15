def group_for_user(user):
    return f"user-{user.pk}"


def group_for_event(event, has_registrations_access):
    return f"event-{'full' if has_registrations_access else 'limited'}-{event.pk}"
