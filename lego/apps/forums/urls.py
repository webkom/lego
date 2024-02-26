# forums/urls.py

from django.urls import path

from .views import ThreadViewSet

urlpatterns = [
    path(
        "<int:forum_id>/threads/",
        ThreadViewSet.as_view({"get": "list", "post": "create"}),
        name="forum-threads-list",
    ),
    path(
        "<int:forum_id>/threads/<int:pk>/",
        ThreadViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="forum-thread-detail",
    ),
]
