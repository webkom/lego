from rest_framework import serializers
from lego.apps.users.models import ChristmasSlotUser, ChristmasSlot

class ChristmasSlotSerializer(serializers.ModelSerializer):
  class Meta:
    model = ChristmasSlot
    fields = ("slot", "info", "answer")
    
class ChristmasSlotUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = ChristmasSlotUser
    fields = ("user", "slot", "completed")