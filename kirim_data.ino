#include <SoftwareSerial.h>
#include <ModbusMaster.h>
#include <DHT.h>

// Definisi pin
#define RX_PIN 2           // RX untuk sensor NPK
#define TX_PIN 3           // TX untuk sensor NPK
#define DHTPIN 4           // Data pin DHT11
#define DHTTYPE DHT11      // Tipe sensor DHT
#define SOIL_MOISTURE_PIN A0 // Analog pin sensor kelembaban tanah

// Inisialisasi komunikasi serial untuk sensor NPK
SoftwareSerial mod(RX_PIN, TX_PIN);
ModbusMaster node;

// Inisialisasi sensor DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  mod.begin(4800);          // Sesuaikan baud rate sensor NPK
  node.begin(1, mod);       // ID Modbus slave sensor NPK
  dht.begin();
}

void loop() {
  // Cek apakah ada permintaan dari NodeMCU
  String minta = "";

  while (Serial.available() > 0) {
    minta += char(Serial.read());
  }

  minta.trim();

  if (minta == "Ya") {
    kirimDataSensor();
  }

  delay(1000);
}

void kirimDataSensor() {
  // Membaca data dari sensor NPK
  uint8_t result = node.readHoldingRegisters(0x001E, 3);
  uint16_t soil_n = 0, soil_p = 0, soil_k = 0;
  bool npk_ok = false;

  if (result == node.ku8MBSuccess) {
    soil_n = node.getResponseBuffer(0);
    soil_p = node.getResponseBuffer(1);
    soil_k = node.getResponseBuffer(2);
    npk_ok = true;
  }

  // Membaca data dari sensor DHT11
  float kelembaban = dht.readHumidity();
  float suhu = dht.readTemperature();
  bool dht_ok = !(isnan(kelembaban) || isnan(suhu));

  // Membaca data dari sensor kelembaban tanah
  int nilaiKelembabanTanah = analogRead(SOIL_MOISTURE_PIN);
  float persenKelembabanTanah = map(nilaiKelembabanTanah, 1023, 0, 0, 100);

  // Gabungkan dan kirim data jika pembacaan sukses
  if (npk_ok && dht_ok) {
    String datakirim = "N:" + String(soil_n) +
                       "#P:" + String(soil_p) +
                       "#K:" + String(soil_k) +
                       "#T:" + String(suhu) +
                       "#H:" + String(kelembaban) +
                       "#SM:" + String(persenKelembabanTanah);

    Serial.println(datakirim);
  } else {
    Serial.println("Gagal membaca salah satu sensor.");
  }
}
