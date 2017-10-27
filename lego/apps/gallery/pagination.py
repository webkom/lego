from lego.utils.pagination import CursorPagination


class GalleryPicturePagination(CursorPagination):

    page_size = 10
    max_page_size = 10
    ordering = 'pk'
