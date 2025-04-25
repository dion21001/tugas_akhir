from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .models import SensorData, FertilizerPrediction, FertilizerWarning
from .serializers import SensorDataSerializer


# Fungsi untuk menampilkan halaman utama

def home(request):
    context = {
        "judul": "Selamat Datang di Aplikasi Prediksi Pupuk",
        "deskripsi": "Aplikasi ini digunakan untuk memprediksi jenis pupuk yang dibutuhkan berdasarkan data sensor.",
    }
    return render(request, "tugas_akhir/index.html",context)
# mengambil data dari sensor dan menyimpannya ke database
class SensorDataView(APIView):
    def post(self, request, *args, **kwargs):
        print("DATA DITERIMA:", request.data)
        serializer = SensorDataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Data berhasil disimpan"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        data = SensorData.objects.all().order_by('-timestamp')  
        serializer = SensorDataSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# Fungsi untuk menampilkan data sensor 
def DataGabungan(request):
    post = SensorData.objects.last()
    prediction = None
    warning_message = None
    if request.method == 'POST':
        soil_type = request.POST.get('soil_type')
        crop_type = request.POST.get('crop_type')
        if post:  
            post.soil_type = soil_type
            post.crop_type = crop_type
            post.save()
    if post:
        if post.soil_type and post.crop_type:
            prediction = FertilizerPrediction.objects.filter(sensor_data=post).first()
            if not prediction:
                fertilizer_warning = FertilizerWarning.objects.filter(sensor_data=post).first()
                if fertilizer_warning:
                    warning_message = fertilizer_warning.warning_message
                else:
                    warning_message = "Data sudah lengkap, namun hasil prediksi belum tersedia. Silakan tunggu."
        else:
            warning_message = "Data belum lengkap. Silakan isi Soil Type dan Crop Type di bawah ini."
    context = {
        "judul": "Data Masukan dan Hasil Prediksi",
        "masukan": post,          
        "prediction": prediction, 
        "warning": warning_message,  
    }
    return render(request, "tugas_akhir/percobaan.html", context)

# Fungsi untuk menampilkan hasil prediksi pupuk
def FertilizerPredictionOnlyView(request):
    predictions = FertilizerPrediction.objects.last()
    context = {
        "judul": "Hasil Prediksi Pupuk",
        "predictions": predictions,
    }
    return render(request, "tugas_akhir/prediksi_saja.html", context)

