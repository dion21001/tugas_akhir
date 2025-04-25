from rest_framework import serializers
from .models import SensorData, FertilizerPrediction

# Serializer untuk model SensorData
class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = [
            'id',
            'temperature',
            'humidity',
            'moisture',
            'nitrogen',
            'phosphorous',
            'potassium',
            'soil_type',   
            'crop_type',   
            'timestamp'
        ]
        read_only_fields = ['id', 'created_at']

# Serializer untuk model FertilizerPrediction
class FertilizerPredictionSerializer(serializers.ModelSerializer):
    sensor_data = SensorDataSerializer(read_only=True)  
    class Meta:
        model = FertilizerPrediction
        fields = [
            'id',  
            'sensor_data',
            'predicted_fertilizer',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
