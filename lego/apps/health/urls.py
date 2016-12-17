from django.conf.urls import url

from .views import HealthView

urlpatterns = [
    url(r'^health/$', HealthView.as_view())
]
