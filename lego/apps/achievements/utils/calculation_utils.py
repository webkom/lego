
import math

from lego.apps.achievements.constants import EVENT_IDENTIFIER, EVENT_PRICE_IDENTIFIER, EVENT_RANK_IDENTIFIER, MEETING_IDENTIFIER, PENALTY_IDENTIFIER, POLL_IDENTIFIER, QUOTE_IDENTIFIER

ACHIEVEMENT_DATA = {
    EVENT_IDENTIFIER: [0, 1, 2, 3, 4, 6], 
    EVENT_RANK_IDENTIFIER: [7, 8, 9],                
    QUOTE_IDENTIFIER: [2],                      
    EVENT_PRICE_IDENTIFIER: [2, 3, 5],                
    MEETING_IDENTIFIER: [2],                  
    POLL_IDENTIFIER: [0, 2, 4],                
    PENALTY_IDENTIFIER: [0, 3, 5, 6],         
}


def calculate_user_rank(user, alpha=0.68, beta=0.45, gamma=0.43, w=0.75):
    N = len(ACHIEVEMENT_DATA)
    highest_rarity = 0
    weighted_rarities_product = 1
    achievement_count = user.achievements.count()

    if achievement_count == 0:
        return 0

    for achievement in user.achievements.all():
        identifier = achievement.identifier
        level = achievement.level

        rarity_list = ACHIEVEMENT_DATA.get(identifier, [])
        rarity = rarity_list[level] if level < len(rarity_list) else 0
        
        highest_rarity = max(highest_rarity, rarity)
        
        weighted_rarity = math.log(rarity + 2) ** 2
        weighted_rarities_product *= weighted_rarity

    G = math.pow(weighted_rarities_product, 1 / achievement_count)
    
    G_normalized = G / (math.log(9 + 2) ** 2)

    baseline = (highest_rarity + 1) / 2

    G_blended = w * G_normalized + (1 - w) * baseline / (math.log(9 + 2) ** 2)

    highest_rarity_component = alpha * (math.sqrt(highest_rarity + 1) / math.sqrt(10))
    geometric_mean_component = beta * G_blended
    achievement_count_component = gamma * (math.log(achievement_count + 1) / math.log(N + 1))

    rank = (100 * (highest_rarity_component + geometric_mean_component + achievement_count_component)) / (alpha + beta + gamma)
    rounded = round(rank, 2)
    return rounded