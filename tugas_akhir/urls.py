from django.urls import path
from . import views

app_name = "tugas"  

urlpatterns = [
    path('sensordata/', views.SensorDataView.as_view(), name='sensor-data'),  # Endpoint API
    path('', views.DataGabungan, name='DataMasukan'),
    path('DataPrediksi/', views.FertilizerPredictionOnlyView, name='DataPrediksi'), 
    
]

