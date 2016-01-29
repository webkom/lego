from django.conf import settings


def site(request):
    """
    Return site information
    """
    return {'SITE': settings.SITE}
