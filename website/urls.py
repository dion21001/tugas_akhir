from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tugas_akhir/',include("tugas_akhir.urls",namespace="tugas"))
]
