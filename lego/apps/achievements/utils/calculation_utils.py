from lego.apps.achievements.constants import (
    COMPLETE_IDENTIFIER,
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
    EVENT_RANK_IDENTIFIER: [7, 8, 9],
    QUOTE_IDENTIFIER: [1],
    EVENT_PRICE_IDENTIFIER: [2, 3, 5],
    MEETING_IDENTIFIER: [1],
    POLL_IDENTIFIER: [0, 2, 4],
    PENALTY_IDENTIFIER: [0, 3, 5, 6],
    EVENT_RULES_IDENTIFIER: [0],
    KEYPRESS_ORDER_IDENTIFIER: [2],
    GENFORS_IDENTIFIER: [0, 2, 4, 5, 7],
    GALA_IDENTIFIER: [0, 3, 5, 6],
    COMPLETE_IDENTIFIER: [1],
}

delta = 0.1
# Remember to update this rarity list when adding new achievement
MAX_POSSIBLE_SCORE = sum(
    max(rarity_list) + 1 + (max(rarity_list) * delta)
    for key, rarity_list in ACHIEVEMENT_RARITIES.items()
    if key != EVENT_RANK_IDENTIFIER
)


def calculate_user_rank(user):
    score = 0.0
    if not user.achievements.exists():
        return 0
    user_achievements = user.achievements.all()
    for achievement in user_achievements:
        rarity_list = ACHIEVEMENT_RARITIES.get(achievement.identifier, [])

        value = rarity_list[achievement.level]
        score += value + 1 + (achievement.level * delta)

    return score if MAX_POSSIBLE_SCORE else 0
