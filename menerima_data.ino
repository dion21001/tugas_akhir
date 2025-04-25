#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <SoftwareSerial.h>

// WiFi credentials
const char* ssid = "TestWiFi";
const char* password = "321321321";
const char* server = "192.168.43.213";  // IP Django server
const int port = 4352;  // GANTI sesuai port server kamu

// SoftwareSerial (RX, TX)
SoftwareSerial DataSerial(12, 13);

// Timing variables
unsigned long previousMillis = 0;
const long interval = 30000; // 5 detik

// Data parsing
String arrData[6];

void setup() {
  Serial.begin(9600);
  DataSerial.begin(9600);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Request data from Arduino Uno
    DataSerial.println("Ya");

    String data = "";

    // Baca data dari serial Uno
    while (DataSerial.available()) {
      char c = DataSerial.read();
      data += c;
    }

    data.trim();

    if (data != "") {
      // Parsing berdasarkan delimiter #
      int index = 0;
      String temp = "";

      for (int i = 0; i <= data.length(); i++) {
        char c = data[i];
        if (c != '#' && i < data.length()) {
          temp += c;
        } else {
          arrData[index++] = temp;
          temp = "";
        }
      }

      // Pastikan jumlah data lengkap (6)
      if (index == 6) {
        // Ambil nilainya
        double nitrogen = arrData[0].substring(2).toFloat();
        double phosphorous = arrData[1].substring(2).toFloat();
        double potassium = arrData[2].substring(2).toFloat();
        double temperature = arrData[3].substring(2).toFloat();
        double humidity = arrData[4].substring(2).toFloat();
        int moisture = arrData[5].substring(3).toInt();

        // Tampilkan ke serial monitor (opsional)
        Serial.println("Parsed Data:");
        Serial.println("N: " + String(nitrogen));
        Serial.println("P: " + String(phosphorous));
        Serial.println("K: " + String(potassium));
        Serial.println("Temperature: " + String(temperature));
        Serial.println("Humidity: " + String(humidity));
        Serial.println("Soil Moisture: " + String(moisture));
        Serial.println();

        // Siapkan JSON
        String jsonData = "{\"temperature\":" + String(temperature, 2) +
                          ",\"humidity\":" + String(humidity, 2) +
                          ",\"moisture\":" + String(moisture) +
                          ",\"nitrogen\":" + String(nitrogen, 2) +
                          ",\"phosphorous\":" + String(phosphorous, 2) +
                          ",\"potassium\":" + String(potassium, 2) + "}";

        // Kirim ke server Django
        WiFiClient client;
        if (client.connect(server, port)) {
          client.println("POST /tugas_akhir/sensordata/ HTTP/1.1");
          client.println("Host: " + String(server));
          client.println("Content-Type: application/json");
          client.print("Content-Length: ");
          client.println(jsonData.length());
          client.println();  // End of headers
          client.println(jsonData);  // JSON payload

          // Print response
          while (client.connected()) {
            while (client.available()) {
              String line = client.readStringUntil('\r');
              Serial.print(line);
            }
          }
          Serial.println();
        } else {
          Serial.println("Connection to server failed");
        }

        client.stop();
      }

      // Bersihkan array
      for (int i = 0; i < 6; i++) {
        arrData[i] = "";
      }
    }
  }
}
