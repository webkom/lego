from datetime import timedelta

from django.utils import timezone

import stripe

from lego.apps.users.models import AbakusGroup, User


def get_dummy_users(n):
    users = []

    for i in range(n):
        first_name = last_name = username = str(i)
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=f"test{i}@aba.wtf",
        )
        user.save()
        AbakusGroup.objects.get(name="Users").add_user(user)
        users.append(user)

    return users


def create_token(number, cvc, year=None):
    if not year:
        year = timezone.now().year + 1
    return stripe.Token.create(
        card={"number": number, "exp_month": 12, "exp_year": year, "cvc": cvc}
    )


def make_penalty_expire(penalty):
    penalty.created_at = timezone.now() - timedelta(days=365)
    penalty.save()
