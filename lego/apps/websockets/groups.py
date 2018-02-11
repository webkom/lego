from channels import Group


def group_for_user(user):
    return Group(f'user-{user.pk}')


def group_for_event(event):
    return Group(f'event-{event.pk}')
