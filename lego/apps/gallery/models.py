from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from lego.apps.comments.models import Comment
from lego.apps.files.models import FileField
from lego.apps.gallery.permissions import GalleryPicturePermissionHandler
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel


class Gallery(BasisModel, ObjectPermissionsModel):
    """
    Image Gallery
    Normal permissions is used to restrict access to the gallery.
    """
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    cover = models.ForeignKey('gallery.GalleryPicture', related_name='gallery_covers',
                              null=True, on_delete=models.SET_NULL)
    location = models.CharField(max_length=64)
    taken_at = models.DateField(null=True)
    photographers = models.ManyToManyField('users.User')

    event = models.ForeignKey('events.Event', related_name='galleries', null=True)


class GalleryPicture(models.Model):
    """
    Store the relation between the gallery and the file in remote storage.
    Inactive element are only visible for users with can_edit permissions.
    """
    gallery = models.ForeignKey(Gallery, related_name='pictures')
    file = FileField(related_name='gallery_pictures')
    taggees = models.ManyToManyField('users.User', blank=True)

    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    comments = GenericRelation(Comment)

    class Meta:
        unique_together = ('gallery', 'file')
        permission_handler = GalleryPicturePermissionHandler()

    @property
    def comment_target(self):
        return '{0}.{1}-{2}'.format(self._meta.app_label, self._meta.model_name, self.pk)

    def __str__(self):
        return f'{self.gallery.title}-#{self.pk}'
