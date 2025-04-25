from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.sensors.sql import SqlSensor
import pandas as pd
import joblib
from sqlalchemy import create_engine
from datetime import timedelta, datetime

# ✅ Load model dan encoder sekali saat DAG pertama kali dibaca
print("🔍 Memuat model dan encoder...")
model = joblib.load("/opt/airflow/dags/output/fertilizer_model_knn.pkl")
fertilizer_encoder = joblib.load("/opt/airflow/dags/output/fertilizer_encoder.pkl")
soil_encoder = joblib.load("/opt/airflow/dags/output/soil_encoder.pkl")
crop_encoder = joblib.load("/opt/airflow/dags/output/crop_encoder.pkl")
print("✅ Model dan encoder berhasil dimuat.")

# ✅ Default arguments DAG
default_args = {
    "owner": "Dion Rikki",
    "retries": 3,
    "retry_delay": timedelta(minutes=3),
}


# ✅ Fungsi untuk mengambil data sensor terbaru yang lengkap dan belum diprediksi
def get_data_from_mysql(**kwargs):
    print("🔍 [1] Mengambil data sensor terbaru yang lengkap dan belum diprediksi...")
    engine = create_engine("mysql+pymysql://root:Pramuka123%40@mysql_api_2:3306/tugas_akhir")

    query = """
    SELECT 
        id, 
        temperature AS Temperature, 
        humidity AS Humidity, 
        moisture AS Moisture, 
        soil_type, 
        crop_type, 
        nitrogen, 
        phosphorous, 
        potassium
    FROM 
        tugas_akhir_sensordata
    WHERE 
        timestamp >= NOW() - INTERVAL 3 MINUTE
        AND soil_type IS NOT NULL
        AND crop_type IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 
            FROM fertilizer_predictions f
            WHERE f.sensor_data_id = tugas_akhir_sensordata.id
        )
    """

    data = pd.read_sql(query, engine)
    print(f"📊 Data ditemukan: {len(data)} baris")
    
    # Push ke XCom
    kwargs['ti'].xcom_push(key="sensor_data", value=data.to_dict(orient="records"))


# ✅ Fungsi prediksi dan penyimpanan hasil ke database
def predict_and_store_result(**kwargs):
    print("🔍 [2] Memproses data dan melakukan prediksi...")
    ti = kwargs['ti']
    data_list = ti.xcom_pull(task_ids='get_data_from_db', key='sensor_data')

    if not data_list:
        print("⚠️ Tidak ada data untuk diproses.")
        return

    # Convert ke DataFrame
    data = pd.DataFrame(data_list)
    print(f"✅ Data siap diproses: {len(data)} baris\n{data.head()}")

    # ✅ Rename kolom agar sesuai dengan model training
    print("📝 Menyesuaikan nama kolom dengan model training...")
    data.rename(columns={
        'nitrogen': 'Nitrogen',
        'phosphorous': 'Phosphorous',
        'potassium': 'Potassium',
        'soil_type': 'Soil_Type',
        'crop_type': 'Crop_Type'
    }, inplace=True)

    # ✅ Encoding Soil_Type dan Crop_Type
    print("🔧 Melakukan encoding kategori Soil_Type dan Crop_Type...")
    try:
        data['Soil_Type'] = soil_encoder.transform(data['Soil_Type'])
        data['Crop_Type'] = crop_encoder.transform(data['Crop_Type'])
    except Exception as e:
        print(f"❌ Gagal saat encoding: {e}")
        return

    # ✅ Menyiapkan fitur sesuai urutan saat training
    print("🧠 Menyiapkan fitur untuk prediksi...")
    ordered_features = ['Temperature', 'Humidity', 'Moisture', 'Soil_Type', 'Crop_Type', 'Nitrogen', 'Potassium', 'Phosphorous']

    try:
        X = data[ordered_features]
    except KeyError as e:
        print(f"❌ Kolom tidak ditemukan: {e}")
        return

    # ✅ Melakukan prediksi
    print("🤖 Menjalankan model prediksi...")
    try:
        y_pred = model.predict(X)
        fertilizer_names = fertilizer_encoder.inverse_transform(y_pred)
        data['predicted_fertilizer'] = fertilizer_names
        print(f"✅ Prediksi selesai:\n{data[['id', 'predicted_fertilizer']]}")
    except Exception as e:
        print(f"❌ Gagal saat prediksi: {e}")
        return

    # ✅ Simpan hasil ke fertilizer_predictions
    print("💾 Menyimpan hasil ke tabel fertilizer_predictions...")
    try:
        engine = create_engine("mysql+pymysql://root:Pramuka123%40@mysql_api_2:3306/tugas_akhir")
        hasil = data[['id', 'predicted_fertilizer']].rename(
            columns={'id': 'sensor_data_id'}
        )
        hasil['created_at'] = datetime.now()  # ✅ Tambahkan kolom created_at
        hasil.to_sql('fertilizer_predictions', engine, if_exists='append', index=False)
        print("✅ Hasil prediksi berhasil disimpan.")
    except Exception as e:
        print(f"❌ Error saat menyimpan ke database: {e}")


# ✅ DAG Definition
with DAG(
    dag_id="perbaikan_skripsi",
    default_args=default_args,
    description="DAG prediksi fertilizer otomatis berdasarkan data sensor terbaru",
    start_date=datetime(2024, 2, 26),
    schedule_interval="*/1 * * * *",  # Setiap 1 menit
    catchup=False,
    tags=["skripsi", "fertilizer", "sensor", "realtime"]
) as dag:

    # 1. Cek ketersediaan data sensor baru
    wait_for_new_data = SqlSensor(
        task_id='wait_for_new_data',
        conn_id='mysql_default',
        sql="""
            SELECT COUNT(*) 
            FROM tugas_akhir_sensordata s
            WHERE s.timestamp >= NOW() - INTERVAL 3 MINUTE
            AND s.soil_type IS NOT NULL
            AND s.crop_type IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 
                FROM fertilizer_predictions f
                WHERE f.sensor_data_id = s.id
            )
        """,
        mode="reschedule",
        poke_interval=60,  # cek setiap 1 menit
        timeout=600,  # maksimal 10 menit menunggu
    )

    # 2. Ambil data sensor dari MySQL
    get_data = PythonOperator(
        task_id='get_data_from_db',
        python_callable=get_data_from_mysql,
    )

    # 3. Prediksi dan simpan hasil ke database
    predict_and_store = PythonOperator(
        task_id='predict_and_store_result',
        python_callable=predict_and_store_result,
    )

    # ✅ Rangkaian task
    wait_for_new_data >> get_data >> predict_and_store
