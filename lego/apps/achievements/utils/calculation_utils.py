from lego.apps.achievements.constants import (
    COMPLETE_IDENTIFIER,
    EASTER_IDENTIFIER,
    EVENT_IDENTIFIER,
    EVENT_PRICE_IDENTIFIER,
    EVENT_RANK_IDENTIFIER,
    EVENT_RULES_IDENTIFIER,
    GALA_IDENTIFIER,
    GENFORS_IDENTIFIER,
    KEYPRESS_ORDER_IDENTIFIER,
    MEETING_IDENTIFIER,
    PENALTY_IDENTIFIER,
    POLL_IDENTIFIER,
    QUOTE_IDENTIFIER,
)

ACHIEVEMENT_RARITIES = {
    EVENT_IDENTIFIER: [0, 1, 2, 3, 4, 6],
    EVENT_RANK_IDENTIFIER: [5, 5, 6],
    QUOTE_IDENTIFIER: [1],
    EVENT_PRICE_IDENTIFIER: [2, 3, 4],
    MEETING_IDENTIFIER: [1],
    POLL_IDENTIFIER: [0, 2, 4],
    PENALTY_IDENTIFIER: [1, 3, 4, 5],
    EVENT_RULES_IDENTIFIER: [0],
    KEYPRESS_ORDER_IDENTIFIER: [2],
    GENFORS_IDENTIFIER: [0, 2, 3, 4, 5],
    GALA_IDENTIFIER: [0, 2, 4, 5],
    COMPLETE_IDENTIFIER: [0],
    EASTER_IDENTIFIER: [2, 2],
}

ACHIEVEMENT_WEIGHTS = {
    EVENT_IDENTIFIER: 1,
    EVENT_RANK_IDENTIFIER: 0.25,
    QUOTE_IDENTIFIER: 1,
    EVENT_PRICE_IDENTIFIER: 1,
    MEETING_IDENTIFIER: 0.33,
    POLL_IDENTIFIER: 0.75,
    PENALTY_IDENTIFIER: 1,
    EVENT_RULES_IDENTIFIER: 0.25,
    KEYPRESS_ORDER_IDENTIFIER: 0.25,
    GENFORS_IDENTIFIER: 0.75,  # These are partially accounted for already in the event_count
    GALA_IDENTIFIER: 0.75,
    COMPLETE_IDENTIFIER: 0.25,
    EASTER_IDENTIFIER: 1,
}

EXCLUDED_ITEMS = [EVENT_RANK_IDENTIFIER, EASTER_IDENTIFIER]

delta = 0.1
# Remember to update this rarity list when adding new achievement
MAX_POSSIBLE_SCORE = sum(
    (max(rarity_list) + 1 + (max(rarity_list) * delta))
    * ACHIEVEMENT_WEIGHTS.get(key, 1)
    for key, rarity_list in ACHIEVEMENT_RARITIES.items()
    if key not in EXCLUDED_ITEMS
)


def calculate_user_rank(user):
    score = 0.0
    if not user.achievements.exists():
        return 0

    user_achievements = user.achievements.all()
    for achievement in user_achievements:
        rarity_list = ACHIEVEMENT_RARITIES.get(achievement.identifier, [])

        value = rarity_list[achievement.level]
        weight = ACHIEVEMENT_WEIGHTS.get(achievement.identifier, 1)

        score += (value + 1 + (achievement.level * delta)) * weight

    return score if MAX_POSSIBLE_SCORE else 0
