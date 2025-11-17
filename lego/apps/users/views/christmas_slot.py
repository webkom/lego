from rest_framework import status, viewsets
from rest_framework.response import Response

from lego.apps.users.models import ChristmasSlot, ChristmasSlotUser
from lego.apps.users.serializers.christmas_slot import ChristmasSlotUserSerializer, ChristmasSlotSerializer

class ChristmasSlotViewSet(viewsets.ModelViewSet):
    queryset = ChristmasSlot.objects.all()
    serializer_class = ChristmasSlotSerializer

    def create(self, request):
        data = request.data
        slot = data.get("slot")
        info = data.get("info")
        answer = data.get("answer")

        _, created = ChristmasSlot.objects.update_or_create(slot=slot, defaults={"info": info, "answer": answer})

        if created:
            return Response(f"Christmas slot {slot} created", status=status.HTTP_201_CREATED)
        return Response(f"Christmas slot {slot} updated", status=status.HTTP_200_OK)

class ChristmasSlotUserViewSet(viewsets.ModelViewSet):
    queryset = ChristmasSlotUser.objects.all()
    serializer_class = ChristmasSlotUserSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user.id)

    def create(self, request):
        try:
            specific_slot = ChristmasSlot.objects.get(slot=request.data.get("slot"))

            if request.data.get("answer") != specific_slot.answer:
                return Response("Wrong answer", status=status.HTTP_200_OK)
            
            for christmas_slot in self.get_queryset():
                if christmas_slot.slot.slot == request.data.get("slot"):
                    return Response(f"Christmas slot {request.data.get('slot')} already exists", status=status.HTTP_200_OK)
            
            ChristmasSlotUser.objects.create(slot=specific_slot, user=self.request.user)
            return Response(f"User {self.request.user} created slot {specific_slot}", status=status.HTTP_201_CREATED)
        except:
            return Response(
                {"error": "Christmas slot does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )