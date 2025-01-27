from lego.utils.pagination import CursorPagination


class AchievementLeaderboardPagination(CursorPagination):
    page_size = 25
    max_page_size = 25
    ordering = "-achievements_score"
