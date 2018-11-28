def group_for_user(user):
    return f"user-{user.pk}"


def group_for_event(event):
    return f"event-{event.pk}"
