#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

// --- KONFIGURACJA WI-FI ---
const char* ssid = "AndroidAP2934";
const char* haslo = "NeroiGucio";

// --- USTALENIE PINÓW ---
const int PIN_SERWO_A = 27;
const int PIN_SERWO_B = 26;
const int PIN_SERWO_C = 25;
const int PIN_MAGNES  = 32;

// Obiekty dla trzech serwomechanizmów
Servo serwoA;
Servo serwoB;
Servo serwoC;

// Pomocnicza funkcja do pobierania wartości z bazy danych dla konkretnego pinu
float pobierzWartoscZSerwera(int pinIndex, float wartoscDomyslna) {
  HTTPClient http;
  // Dynamicznie podstawiamy numer pinu (joint_index) do adresu URL
  String url = "http://ipzelektromagnes.pythonanywhere.com/device/1/joint/" + String(pinIndex) + "/latest";
  http.begin(url);
  
  int httpCode = http.GET();
  float wyjściowaWartosc = wartoscDomyslna;

  if (httpCode == 200) {
    String payload = http.getString();
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (!error) {
      wyjściowaWartosc = doc["value"];
    }
  } else {
    Serial.print("Błąd pobierania dla pinu ");
    Serial.print(pinIndex);
    Serial.print(" - Status HTTP: ");
    Serial.println(httpCode);
  }
  
  http.end();
  return wyjściowaWartosc;
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // 1. Inicjalizacja trzech serwomechanizmów
  serwoA.attach(PIN_SERWO_A, 500, 2400);
  serwoB.attach(PIN_SERWO_B, 500, 2400);
  serwoC.attach(PIN_SERWO_C, 500, 2400);
  
  // Ustawienie pozycji startowych (90 stopni = bezpieczny środek / stop)
  serwoA.write(90);
  serwoB.write(90);
  serwoC.write(90);

  // 2. Inicjalizacja pinu elektromagnesu jako WYJŚCIE
  pinMode(PIN_MAGNES, OUTPUT);
  digitalWrite(PIN_MAGNES, LOW); // Na starcie magnes wyłączony

  // 3. Łączenie z Wi-Fi
  WiFi.begin(ssid, haslo);
  Serial.print("Łączenie z Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nPołączono z Wi-Fi! Robot gotowy do pracy.");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    
    // --- 1. OBSŁUGA SERWA A (Pin 27) ---
    float katA = pobierzWartoscZSerwera(27, 90.0);
    if (katA >= 0 && katA <= 180) {
      serwoA.write((int)katA);
    }

    // --- 2. OBSŁUGA SERWA B (Pin 26) ---
    float katB = pobierzWartoscZSerwera(26, 90.0);
    if (katB >= 0 && katB <= 180) {
      serwoB.write((int)katB);
    }

    // --- 3. OBSŁUGA SERWA C (Pin 25) ---
    float katC = pobierzWartoscZSerwera(25, 90.0);
    if (katC >= 0 && katC <= 180) {
      serwoC.write((int)katC);
    }

    // --- 4. OBSŁUGA ELEKTROMAGNESU (Pin 32 / w panelu oznaczony jako 99) ---
    float stanMagnesu = pobierzWartoscZSerwera(99, 0.0);
    if (stanMagnesu == 1.0) {
      digitalWrite(PIN_MAGNES, HIGH); // Włącz przekaźnik / tranzystor magnesu
      Serial.println("Magnes: WŁĄCZONY");
    } else {
      digitalWrite(PIN_MAGNES, LOW);  // Wyłącz
      Serial.println("Magnes: WYŁĄCZONY");
    }

    // Podgląd diagnostyczny w Serial Monitorze
    Serial.printf("Pozycje -> A: %.0f° | B: %.0f | C: %.0f\n", katA, katB, katC);
    Serial.println("----------------------------------------");
  }
  
  delay(800); // Odpytuj bazę danych o cały komplet poleceń co niecałą sekundę
