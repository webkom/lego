from collections.abc import Callable
from typing import Any, TypedDict

from lego.apps.achievements.verification import (
    check_complete_profile,
    check_event_generic,
    check_longest_period_without_penalties,
    check_poll_responses,
    check_total_event_payment_over,
    check_total_galas,
    check_total_genfors_events,
    check_verified_quote,
)
from lego.apps.users.models import User


class Achievement(TypedDict):
    identifier: str
    requirement_function: Callable[[User, Any], bool]
    level: int


AchievementCollection = dict[str, Achievement]

# Remember to update rarity list in /utils/calculation_utils.py when adding new achievement

EVENT_IDENTIFIER = "event_count"
EVENT_RANK_IDENTIFIER = "event_rank"
EVENT_PRICE_IDENTIFIER = "event_price"
EVENT_RULES_IDENTIFIER = "event_rules"
KEYPRESS_ORDER_IDENTIFIER = "keypress_order"
QUOTE_IDENTIFIER = "quote_count"
MEETING_IDENTIFIER = "meeting_hidden"
POLL_IDENTIFIER = "poll_count"
PENALTY_IDENTIFIER = "penalty_period"
GENFORS_IDENTIFIER = "genfors_count"
GALA_IDENTIFIER = "gala_count"
COMPLETE_IDENTIFIER = "complete_profile"

GALA_SUBSTRINGS = (
    "bankett",  # Max 3 (itDAGENE)
    "immatrikuleringsball",  # Max 5
    "jubileum",  # Max 4 (Abakus, Abakusrevyen, LaBamba, readme)
    "julebord",  # Max 5
    "vaargalla",  # Max 5
)

EVENT_ACHIEVEMENTS: AchievementCollection = {
    "arrangement_10": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=10),
        "level": 0,
    },
    "arrangement_25": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=25),
        "level": 1,
    },
    "arrangement_50": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=50),
        "level": 2,
    },
    "arrangement_100": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=100),
        "level": 3,
    },
    "arrangement_150": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=150),
        "level": 4,
    },
    "arrangement_200": {
        "identifier": EVENT_IDENTIFIER,
        "requirement_function": lambda user: check_event_generic(user=user, count=200),
        "level": 5,
    },
}

EVENT_RANK_ACHIEVEMENTS: AchievementCollection = {
    "event_rank_3": {
        "identifier": EVENT_RANK_IDENTIFIER,
        "requirement_function": lambda user: False,
        "level": 0,
    },
    "event_rank_2": {
        "identifier": EVENT_RANK_IDENTIFIER,
        "requirement_function": lambda user: False,
        "level": 1,
    },
    "event_rank_1": {
        "identifier": EVENT_RANK_IDENTIFIER,
        "requirement_function": lambda user: False,
        "level": 2,
    },
}

QUOTE_ACHIEVEMENTS: AchievementCollection = {
    "quote_1": {
        "identifier": QUOTE_IDENTIFIER,
        "requirement_function": lambda user: check_verified_quote(user=user),
        "level": 0,
    },
}

COMPLETE_ACHIEVEMENT: AchievementCollection = {
    "complete_1": {
        "identifier": COMPLETE_IDENTIFIER,
        "requirement_function": lambda user: check_complete_profile(user=user),
        "level": 0,
    },
}

EVENT_PRICE_ACHIEVEMENTS: AchievementCollection = {
    "price_1": {
        "identifier": EVENT_PRICE_IDENTIFIER,
        "requirement_function": lambda user: check_total_event_payment_over(
            user=user, price=250000
        ),
        "level": 0,
    },
    "price_2": {
        "identifier": EVENT_PRICE_IDENTIFIER,
        "requirement_function": lambda user: check_total_event_payment_over(
            user=user, price=500000
        ),
        "level": 1,
    },
    "price_3": {
        "identifier": EVENT_PRICE_IDENTIFIER,
        "requirement_function": lambda user: check_total_event_payment_over(
            user=user, price=1000000
        ),
        "level": 2,
    },
}

MEETING_ACHIEVEMENTS: AchievementCollection = {
    "meeting_hidden": {
        "identifier": MEETING_IDENTIFIER,
        "requirement_function": lambda user: False,
        "level": 0,
    },
}

EVENT_RULES: AchievementCollection = {
    "event_rules": {
        "identifier": EVENT_RULES_IDENTIFIER,
        "requirement_function": lambda user: False,
        "level": 0,
    },
}

POLL_ACHIEVEMENTS: AchievementCollection = {
    "poll_5": {
        "identifier": POLL_IDENTIFIER,
        "requirement_function": lambda user: check_poll_responses(user=user, count=5),
        "level": 0,
    },
    "poll_25": {
        "identifier": POLL_IDENTIFIER,
        "requirement_function": lambda user: check_poll_responses(user=user, count=25),
        "level": 1,
    },
    "poll_50": {
        "identifier": POLL_IDENTIFIER,
        "requirement_function": lambda user: check_poll_responses(user=user, count=50),
        "level": 2,
    },
}

PENALTY_ACHIEVEMENTS: AchievementCollection = {
    "penalty_1": {
        "identifier": PENALTY_IDENTIFIER,
        "requirement_function": lambda user: check_longest_period_without_penalties(
            user=user, years=1
        ),
        "level": 0,
    },
    "penalty_2": {
        "identifier": PENALTY_IDENTIFIER,
        "requirement_function": lambda user: check_longest_period_without_penalties(
            user=user, years=2
        ),
        "level": 1,
    },
    "penalty_3": {
        "identifier": PENALTY_IDENTIFIER,
        "requirement_function": lambda user: check_longest_period_without_penalties(
            user=user, years=3
        ),
        "level": 2,
    },
    "penalty_4": {
        "identifier": PENALTY_IDENTIFIER,
        "requirement_function": lambda user: check_longest_period_without_penalties(
            user=user, years=4
        ),
        "level": 3,
    },
}

GENFORS_ACHIEVEMENTS: AchievementCollection = {
    "genfors_1": {
        "identifier": GENFORS_IDENTIFIER,
        "requirement_function": lambda user: check_total_genfors_events(
            user=user, count=1
        ),
        "level": 0,
    },
    "genfors_2": {
        "identifier": GENFORS_IDENTIFIER,
        "requirement_function": lambda user: check_total_genfors_events(
            user=user, count=3
        ),
        "level": 1,
    },
    "genfors_3": {
        "identifier": GENFORS_IDENTIFIER,
        "requirement_function": lambda user: check_total_genfors_events(
            user=user, count=6
        ),
        "level": 2,
    },
    "genfors_4": {
        "identifier": GENFORS_IDENTIFIER,
        "requirement_function": lambda user: check_total_genfors_events(
            user=user, count=8
        ),
        "level": 3,
    },
    "genfors_5": {
        "identifier": GENFORS_IDENTIFIER,
        "requirement_function": lambda user: check_total_genfors_events(
            user=user, count=10
        ),
        "level": 4,
    },
}

GALA_ACHIEVEMENTS: AchievementCollection = {
    "gala_1": {
        "identifier": GALA_IDENTIFIER,
        "requirement_function": lambda user: check_total_galas(user=user, count=1),
        "level": 0,
    },
    "gala_5": {
        "identifier": GALA_IDENTIFIER,
        "requirement_function": lambda user: check_total_galas(user=user, count=5),
        "level": 1,
    },
    "gala_10": {
        "identifier": GALA_IDENTIFIER,
        "requirement_function": lambda user: check_total_galas(user=user, count=10),
        "level": 2,
    },
    "gala_15": {
        "identifier": GALA_IDENTIFIER,
        "requirement_function": lambda user: check_total_galas(user=user, count=15),
        "level": 3,
    },
}

KEYPRESS_ORDER: AchievementCollection = {
    "keypress_order": {
        "identifier": KEYPRESS_ORDER_IDENTIFIER,
        "requirement_function": lambda user: False,
        "level": 0,
    },
}


HIDDEN_ACHIEVEMENTS = {
    **QUOTE_ACHIEVEMENTS,
    **MEETING_ACHIEVEMENTS,
    **KEYPRESS_ORDER,
    **COMPLETE_ACHIEVEMENT,
}

ACHIEVEMENTS = {
    **EVENT_ACHIEVEMENTS,
    **EVENT_RANK_ACHIEVEMENTS,
    **EVENT_PRICE_ACHIEVEMENTS,
    **EVENT_RULES,
    **POLL_ACHIEVEMENTS,
    **HIDDEN_ACHIEVEMENTS,
    **PENALTY_ACHIEVEMENTS,
    **GENFORS_ACHIEVEMENTS,
    **GALA_ACHIEVEMENTS,
}

ACHIEVEMENT_IDENTIFIERS = sorted(
    {(value["identifier"], value["identifier"]) for value in ACHIEVEMENTS.values()}
)
