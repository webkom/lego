from lego.apps.users.models import AbakusGroup, User


def create_normal_user():
    return User.objects.create(username='normal_user')


def create_super_user():
    user = User.objects.create(username='super_user')
    group = AbakusGroup.objects.create(name='super_group', permissions=['/sudo/'])
    group.add_user(user)
    return user
