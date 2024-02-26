from django.conf import settings
from django.conf.urls import include
from django.http import Http404, HttpResponseRedirect
from django.urls import re_path, resolve
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from .v1 import urlpatterns as v1_urlpatterns


@csrf_exempt
def version_redirect(request, path):
    new_path = f"/api/{settings.API_VERSION}/{path}/"

    match = resolve(new_path)

    if match.func == version_redirect:
        raise Http404

    return HttpResponseRedirect(new_path)


app_name = "api"
urlpatterns = [
    re_path(r"^v1/", include((v1_urlpatterns, "v1"), namespace="v1")),
    re_path(
        r"^$", RedirectView.as_view(url=f"/api/{settings.API_VERSION}/"), name="default"
    ),
    re_path(r"^(.*)/$", version_redirect),
]
