from django.db import models

from lego.apps.files.models import FileField
from lego.apps.permissions.models import ObjectPermissionsModel
from lego.utils.models import BasisModel

from .permissions import GalleryPicturePermissionHandler


class Gallery(BasisModel, ObjectPermissionsModel):
    """
    Image Gallery
    Normal permissions is used to restrict access to the gallery.
    """
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    cover = models.ForeignKey('gallery.GalleryPicture', related_name='gallery_covers', null=True)
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

    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('gallery', 'file')
        permission_handler = GalleryPicturePermissionHandler()
