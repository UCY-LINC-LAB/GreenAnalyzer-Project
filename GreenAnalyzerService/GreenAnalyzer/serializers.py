from .models import RESModel, EnergyProfile
from rest_framework import serializers
from services import modeler


class RESSerializer(serializers.ModelSerializer):

    class Meta:
        model = RESModel
        fields = '__all__'

    def validate(self, data):
        model_type = data.get('model_type')
        optimize_metric = data.get('optimize_metric')
        panel_tilt = data.get('panel_tilt')
        panel_size = data.get('panel_size')

        if model_type == 'AI' and not optimize_metric:
            raise serializers.ValidationError({'optimize_metric': 'This field is required when model_type is AI.'})
        
        if model_type == 'MATH' and not panel_tilt:
            raise serializers.ValidationError({'panel_tilt': 'This field is required when model_type is MATH.'})
        
        if model_type == 'MATH' and not panel_size:
            raise serializers.ValidationError({'panel_size': 'This field is required when model_type is MATH.'})

        return data

class EnergyProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = EnergyProfile
        fields = '__all__'