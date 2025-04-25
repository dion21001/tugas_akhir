from django import forms
from .models import SensorData, FertilizerPrediction

# Form untuk input atau update data sensor
class SensorDataForm(forms.ModelForm):
    class Meta:
        model = SensorData
        fields = [
            'temperature',
            'humidity',
            'moisture',
            'nitrogen',
            'phosphorous',
            'potassium',
            'soil_type',
            'crop_type'
        ]
        widgets = {
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Temperature'}),
            'humidity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Humidity'}),
            'moisture': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Moisture'}),
            'nitrogen': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Nitrogen (optional)'}),
            'phosphorous': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Phosphorous (optional)'}),
            'potassium': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Potassium (optional)'}),
            'soil_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Soil Type (optional)'}),
            'crop_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Crop Type (optional)'}),
        }


# Form untuk input atau update hasil prediksi (fertilizer prediction)
class FertilizerPredictionForm(forms.ModelForm):
    class Meta:
        model = FertilizerPrediction
        fields = [
            'sensor_data',  # Foreign key ke SensorData
            'predicted_fertilizer'
        ]
        widgets = {
            'sensor_data': forms.Select(attrs={'class': 'form-control'}),
            'predicted_fertilizer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Predicted Fertilizer'}),
        }
