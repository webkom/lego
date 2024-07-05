from django.urls import path

from .views import LendableObjectViewSet

urlpatterns = [
    path(
        "lendableobject/<int:pk>/lendinginstances/",
        LendableObjectViewSet.as_view({"get": "lendingInstance"}),
        name="lendableobject-lendinginstance",
    ),
]
