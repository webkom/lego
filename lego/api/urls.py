from django.conf import settings
from django.conf.urls import include, url
from django.core.urlresolvers import resolve
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from .v1 import events_router as v1_events
from .v1 import pools_router as v1_pools
from .v1 import router as v1


@csrf_exempt
def version_redirect(request, path):
    new_path = '/api/{0}/{1}/'.format(settings.API_VERSION, path)

    match = resolve(new_path)

    if match.func == version_redirect:
        raise Http404

    return HttpResponseRedirect(new_path)

urlpatterns = [
    url(r'^v1/', include(v1.urls)),
    url(r'^v1/', include(v1_events.urls)),
    url(r'^v1/', include(v1_pools.urls)),
    url(r'^(.*)/$', version_redirect),
]
