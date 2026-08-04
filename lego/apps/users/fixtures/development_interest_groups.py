"""
Interest groups seeded in development only.

Production groups live in initial_abakus_groups.py - these exist so the
development fixtures (leader memberships, interest events) have groups to
reference, without fake groups ending up in the production seed data. The
pks are far above the initial group range so they can never collide with
real groups added later.
"""

from lego.apps.users import constants
from lego.apps.users.models import AbakusGroup

# (pk, name, description, active) - these groups fill the interest group
# grid in development; the development events and memberships reference the
# four interest groups that already exist in the initial tree
DEVELOPMENT_INTEREST_GROUPS = [
    (9070, "Abasjakk", "lynsjakk og turneringer", True),
    (9071, "Ababrygg", "hjemmebrygging", True),
    (9072, "Abapadel", "padel for alle nivåer", True),
    (9073, "Abaski", "topptur og alpint", True),
    (9074, "Abasykkel", "landevei og terreng", True),
    (9075, "Abafilm", "filmkvelder med popkorn", True),
    (9076, "Abaquiz", "quizlag på byen", True),
    (9077, "Abakaffe", "kaffebrygging tatt litt for seriøst", True),
    (9078, "Abafoto", "foto og mørkerom", True),
    (9079, "Abagolf", "golfsimulator og bane", True),
    (9080, "Abayoga", "rolig start på dagen", True),
    (9081, "Abastrikk", "strikk og drikk", True),
    (9082, "Abaspill", "brettspill og kortspill", True),
    (9083, "Abamat", "matlaging og middagsklubb", True),
    (9084, "Abafjell", "fjellturer og friluftsliv", True),
    (9085, "Abadans", "swing og salsa", True),
    (9086, "Abadykk", "dykking og fridykking", True),
    (9087, "Abacurling", "curling på Leangen", False),
    (9088, "Abavolley", "volleyball", False),
    (9089, "Abatennis", "tennis i sommerhalvåret", False),
]


def load_development_interest_groups() -> None:
    parent = AbakusGroup.objects.get(name="Interessegrupper")
    for pk, name, description, active in DEVELOPMENT_INTEREST_GROUPS:
        AbakusGroup.objects.update_or_create(
            pk=pk,
            defaults={
                "name": name,
                "description": description,
                "type": constants.GROUP_INTEREST,
                "parent": parent,
                "active": active,
            },
        )
