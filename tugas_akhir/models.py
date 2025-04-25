from django.db import models
from django.utils import timezone

from django.db import models
from django.utils import timezone

# membuat model untuk menyimpan data sensor
class SensorData(models.Model):
    temperature = models.FloatField()
    humidity = models.FloatField()
    moisture = models.IntegerField()
    nitrogen = models.FloatField(null=True, blank=True)
    phosphorous = models.FloatField(null=True, blank=True)
    potassium = models.FloatField(null=True, blank=True)
    soil_type = models.CharField(max_length=50, null=True, blank=True)  
    crop_type = models.CharField(max_length=50, null=True, blank=True)  
    timestamp = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"SensorData ID: {self.id} | Temp: {self.temperature}, Humidity: {self.humidity}, Moisture: {self.moisture}"

# membuat model untuk menyimpan hasil prediksi pupuk
class FertilizerPrediction(models.Model):
    sensor_data = models.OneToOneField(
        SensorData,
        on_delete=models.CASCADE,
        related_name='fertilizer_prediction',
        null=True
    )
    predicted_fertilizer = models.CharField(max_length=50, default="Unknown")  
    created_at = models.DateTimeField(default=timezone.now)  

    class Meta:
        db_table = 'fertilizer_predictions'  
    def __str__(self):
        return f"Prediction for SensorData ID: {self.sensor_data.id} -> Fertilizer: {self.predicted_fertilizer}"

class FertilizerWarning(models.Model):
    sensor_data = models.OneToOneField(
        SensorData,
        on_delete=models.CASCADE,
        related_name='fertilizer_warning',
        null=True
    )  

    warning_message = models.TextField()  
    created_at = models.DateTimeField(default=timezone.now)  

    class Meta:
        db_table = 'fertilizer_warnings'  

    def __str__(self):
        return f"Warning for SensorData ID: {self.sensor_data.id} -> {self.warning_message}"
