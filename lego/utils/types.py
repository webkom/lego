from typing import Union

from django.urls import URLPattern, URLResolver

# For urlpatterns
URLList = list[Union[URLPattern, URLResolver]]
