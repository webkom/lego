from django.db import models


class SearchTestModel(models.Model):
    """
    This model is used for testing only.
    This may be a bit overkill but it makes testing much easier.
    """
    title = models.CharField(max_length=100)
    description = models.TextField()
