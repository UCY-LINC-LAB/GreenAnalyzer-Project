from .models import RESModel, EnergyProfile
from rest_framework import serializers
from services import modeler


class RESSerializer(serializers.ModelSerializer):

    class Meta:
        model = RESModel
        fields = '__all__'

class EnergyProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = EnergyProfile
        fields = '__all__'