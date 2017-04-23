from datetime import timedelta

import stripe
from django.utils import timezone

from lego.apps.users.models import AbakusGroup, User


def get_dummy_users(n):
    users = []

    for i in range(n):
        first_name = last_name = username = email = str(i)
        user = User(username=username, first_name=first_name, last_name=last_name, email=email)
        user.save()
        AbakusGroup.objects.get(name='Users').add_user(user)
        users.append(user)

    return users


def create_token(number, cvc, year=None):
    if not year:
        year = timezone.now().year + 1
    return stripe.Token.create(
        card={
            'number': number,
            'exp_month': 12,
            'exp_year': year,
            'cvc': cvc
        },
    )


def make_penalty_expire(penalty):
    penalty.created_at = timezone.now() - timedelta(days=365)
    penalty.save()
