from mptt.templatetags.mptt_tags import cache_tree_children
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lego.users.models import AbakusGroup
from lego.users.permissions import AbakusGroupPermissions
from lego.users.serializers import AbakusGroupSerializer, PublicAbakusGroupSerializer


def build_tree(nodes):
    tree = []
    for node in nodes:
        serializer = PublicAbakusGroupSerializer(node)
        tree.append({
            'children': build_tree(node.get_children()),
            'group': serializer.data
        })

    return tree


class AbakusGroupViewSet(viewsets.ModelViewSet):
    queryset = AbakusGroup.objects.all()
    serializer_class = AbakusGroupSerializer
    permission_classes = (IsAuthenticated, AbakusGroupPermissions)

    @list_route(methods=['GET'])
    def hierarchy(self, request):
        # mptt 0.8 requires the QuerySet to be ordered by tree_id and lft:
        top_nodes = cache_tree_children(self.queryset.order_by('tree_id', 'lft'))
        tree = build_tree(top_nodes)
        return Response(data=tree)
