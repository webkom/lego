from rest_framework import serializers
from lego.apps.users.models import ChristmasSlotUser, ChristmasSlot

class ChristmasSlotSerializer(serializers.ModelSerializer):
  class Meta:
    model = ChristmasSlot
    fields = ("slot",)
    
class ChristmasSlotUserSerializer(serializers.ModelSerializer):
  slot = ChristmasSlotSerializer()
  class Meta:
    model = ChristmasSlotUser
    fields = ("user", "slot")