from abc import abstractproperty

from celery_haystack.indexes import CelerySearchIndex
from haystack import indexes


class SearchIndex(CelerySearchIndex):

    search_text = indexes.CharField(document=True, use_template=True)

    @abstractproperty
    def get_model(self):
        raise NotImplementedError

    @abstractproperty
    def index_queryset(self, using=None):
        raise NotImplementedError

    class Meta:
        abstract = True
