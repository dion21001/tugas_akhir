from django.contrib import admin
from .models import SensorData,FertilizerPrediction # Impor model SensorData

# Mendaftarkan model ke admin panel
admin.site.register(SensorData)
admin.site.register(FertilizerPrediction)