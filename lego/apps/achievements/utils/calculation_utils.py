
import math

ACHIEVEMENT_DATA = {
    "event_count": [0, 1, 2, 3, 4, 6], 
    "event_rank": [7, 8, 9],                
    "quote_count": [2],                      
    "event_price": [2, 3, 5],                
    "meeting_hidden": [2],                  
    "poll_count": [0, 2, 4],                
    "penalty_period": [0, 3, 5, 6],         
}


def calculate_user_rank(user):
    alpha = 0.55
    beta = 0.45
    gamma = 0.35
    N = len(ACHIEVEMENT_DATA)
    highest_rarity = 0
    normalized_rarities_product = 1
    achievement_count = user.achievements.count()

    if achievement_count == 0:
        return 0

    for achievement in user.achievements.all():
        identifier = achievement.identifier
        level = achievement.level

        rarity_list = ACHIEVEMENT_DATA.get(identifier, [])
        
        rarity = rarity_list[level] if level < len(rarity_list) else 0
        
        highest_rarity = max(highest_rarity, rarity)
        normalized_rarity = (rarity + 1) / 10
        normalized_rarities_product *= normalized_rarity

    G = math.pow(normalized_rarities_product, 1 / achievement_count)

    highest_rarity_component = alpha * (math.sqrt(highest_rarity + 1) / math.sqrt(10))
    geometric_mean_component = beta * G
    achievement_count_component = gamma * (math.log(achievement_count + 1) / math.log(N + 1))

    rank = (4 * (highest_rarity_component + geometric_mean_component + achievement_count_component)) / (alpha + beta + gamma)

    return rank