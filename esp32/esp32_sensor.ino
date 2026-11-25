#include <Wire.h>
#include <DFRobot_ADS1115.h>
#include <DFRobot_RainfallSensor.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <esp_system.h>
#include <math.h>

#include "wifi_config.h"

//CONFIG

// Interwał pomiarów
static constexpr uint32_t MEASUREMENT_INTERVAL_MIN = 30;

static constexpr uint32_t MEASUREMENT_INTERVAL_MS =
    MEASUREMENT_INTERVAL_MIN * 60UL * 1000UL;
static constexpr uint32_t RAIN_CHECK_INTERVAL_MS = 1000;

// Piny
static constexpr uint8_t PIN_ONEWIRE = 4;
static constexpr uint8_t PIN_SDA = 21;
static constexpr uint8_t PIN_SCL = 22;
static constexpr uint8_t PIN_SENSOR_MODE = 32;

// Wi-Fi
static constexpr uint32_t WIFI_TIMEOUT_MS = 20000;
static constexpr uint32_t WIFI_RETRY_DELAY_MS = 500;

// HTTP
static constexpr uint8_t HTTP_MAX_ATTEMPTS = 3;
static constexpr uint32_t HTTP_TIMEOUT_MS = 8000;

// Kalibracja pH
static constexpr float PH_V_AT_4 = 3.00f;
static constexpr float PH_V_AT_7 = 2.50f;

// Kalibracja EC
static constexpr float EC_V_AT_1413 = 1.00f;
static constexpr float EC_V_AT_12880 = 2.00f;

// Kalibracja czujników
static constexpr bool SENSOR_CALIBRATION_COMPLETE = true;


static constexpr uint32_t RTC_MAGIC_VALUE = 0xAD2026A1;

RTC_DATA_ATTR uint32_t rtcMagic = 0;
RTC_DATA_ATTR bool hasPendingReading = false;
RTC_DATA_ATTR char pendingJson[512] = {0};


DFRobot_ADS1115 ads(&Wire);

DFRobot_RainfallSensor_I2C rain(&Wire);

OneWire oneWire(PIN_ONEWIRE);

DallasTemperature temperatureSensor(&oneWire);

bool measurementSensorsInitialized = false;
bool measurementMode = false;
uint32_t lastMeasurementMs = 0;
uint32_t lastRainCheckMs = 0;
float lastRainfall = NAN;



// Odczyt napięcia ADS1115
float readVoltage(uint8_t channel) {
    return ads.readVoltage(channel) / 1000.0f;
}

// Przeliczanie pH
float readPH(float voltage) {
    return 7.0f +
           (voltage - PH_V_AT_7) * 3.0f /
           (PH_V_AT_7 - PH_V_AT_4);
}

// Przeliczanie EC
float readEC(float voltage) {
    return 1413.0f +
           (voltage - EC_V_AT_1413) *
           (12880.0f - 1413.0f) /
           (EC_V_AT_12880 - EC_V_AT_1413);
}

// Przybliżona charakterystyka turbidity
float readTurbidityNTU(float voltage) {
    return -1120.4f * voltage * voltage +
           5742.3f * voltage -
           4353.8f;
}

// Generowanie identyfikatora UUID
void generateMeasurementId(char* output) {

    uint8_t bytes[16];

    for (uint8_t i = 0; i < 16; i += 4) {
        uint32_t randomValue = esp_random();

        memcpy(&bytes[i], &randomValue, 4);
    }

    // UUID v4
    bytes[6] = (bytes[6] & 0x0F) | 0x40;
    bytes[8] = (bytes[8] & 0x3F) | 0x80;

    snprintf(
        output,
        37,
        "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
        bytes[0], bytes[1], bytes[2], bytes[3],
        bytes[4], bytes[5],
        bytes[6], bytes[7],
        bytes[8], bytes[9],
        bytes[10], bytes[11], bytes[12],
        bytes[13], bytes[14], bytes[15]
    );
}


void initializeRainSensor() {
    Wire.begin(PIN_SDA, PIN_SCL);
    rain.begin();
}

void initializeMeasurementSensors() {
    // ADS1115
    ads.setAddr_ADS1115(ADS1115_IIC_ADDRESS0);
    ads.init();
    ads.setGain(eGAIN_TWOTHIRDS);
    ads.setMode(eMODE_SINGLE);
    ads.setRate(eRATE_128);
    ads.setOSMode(eOSMODE_SINGLE);

    // Temperatura
    temperatureSensor.begin();

}



bool connectWiFi() {

    Serial.println("Laczenie z Wi-Fi...");

    WiFi.mode(WIFI_STA);

    WiFi.begin(AD_WIFI_SSID, AD_WIFI_PASSWORD);

    const uint32_t startTime = millis();

    while (WiFi.status() != WL_CONNECTED) {

        if (millis() - startTime >= WIFI_TIMEOUT_MS) {

            Serial.println("Timeout Wi-Fi!");

            WiFi.disconnect(true);
            WiFi.mode(WIFI_OFF);

            return false;
        }

        delay(WIFI_RETRY_DELAY_MS);
    }

    Serial.println("Wi-Fi polaczone!");

    Serial.print("IP: ");
    Serial.println(WiFi.localIP());

    return true;
}

// Wyłączenie Wi-Fi
void disconnectWiFi() {

    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);

    delay(100);
}



bool sendPendingReading() {

    if (!hasPendingReading) {
        return true;
    }

    if (WiFi.status() != WL_CONNECTED) {
        return false;
    }

    HTTPClient http;

    http.setTimeout(HTTP_TIMEOUT_MS);

    if (!http.begin(AD_GATEWAY_URL)) {
        Serial.println("Blad inicjalizacji HTTP!");
        return false;
    }

    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-ESP32-Token", AD_LOCAL_TOKEN);

    bool success = false;

    for (uint8_t attempt = 1;
         attempt <= HTTP_MAX_ATTEMPTS;
         attempt++) {

        Serial.printf(
            "Wysylanie danych - proba %u/%u\n",
            attempt,
            HTTP_MAX_ATTEMPTS
        );

        const int status = http.POST(
            reinterpret_cast<uint8_t*>(pendingJson),
            strlen(pendingJson)
        );

        Serial.printf("HTTP status: %d\n", status);

        if (status == 200 || status == 202) {

            success = true;

            Serial.println("Dane wyslane!");

            break;
        }

        if (attempt < HTTP_MAX_ATTEMPTS) {
            delay(1000);
        }
    }

    http.end();

    if (success) {

        hasPendingReading = false;

        memset(pendingJson, 0, sizeof(pendingJson));

    } else {

        Serial.println("Nie udalo sie wyslac danych.");
        Serial.println("Pomiar pozostaje w pamieci RTC.");
    }

    return success;
}



bool performMeasurement() {

    Serial.println();
    Serial.println("================================");
    Serial.println("ROZPOCZYNAM POMIAR AD");
    Serial.println("================================");

    // Temperatura
    temperatureSensor.requestTemperatures();

    const float temp =
        temperatureSensor.getTempCByIndex(0);

    // Napięcia czujników analogowych
    const float phVoltage = readVoltage(0);
    const float ecVoltage = readVoltage(1);
    const float turbidityVoltage = readVoltage(2);

    // Przeliczanie wartości
    const float ph = readPH(phVoltage);
    const float ec = readEC(ecVoltage);
    const float turbidityNtu =
        readTurbidityNTU(turbidityVoltage);

    // Opad
    const float rainfall = rain.getRainfall();
    const float rainfall1h = rain.getRainfall(1);

    // Tworzenie JSON
    StaticJsonDocument<384> document;

    document["sensor_id"] = WiFi.macAddress();

    char measurementId[37];

    generateMeasurementId(measurementId);

    document["measurement_id"] = measurementId;

    // Temperatura
    if (temp != DEVICE_DISCONNECTED_C && isfinite(temp)) {
        document["temperature"] = temp;
    }

    // pH
    if (SENSOR_CALIBRATION_COMPLETE &&
        isfinite(ph) && ph >= 0 && ph <= 14) {

        document["ph"] = ph;
    }

    // EC
    if (SENSOR_CALIBRATION_COMPLETE &&
        isfinite(ec) && ec >= 0 && ec <= 3000) {

        document["ec"] = ec;
    }

    // Mętność
    if (isfinite(turbidityNtu) &&
        turbidityNtu >= 0 && turbidityNtu <= 3000) {

        document["turbidity_ntu"] = turbidityNtu;
    }

    // Opad całkowity
    if (isfinite(rainfall) && rainfall >= 0) {
        document["rainfall_mm"] = rainfall;
    }

    // Opad z ostatniej godziny
    if (isfinite(rainfall1h) && rainfall1h >= 0) {
        document["rainfall_1h_mm"] = rainfall1h;
    }

    // Zapis danych do pamięci RTC
    const size_t written =
        serializeJson(document, pendingJson, sizeof(pendingJson));

    if (written == 0) {

        Serial.println("Blad zapisu JSON!");

        return false;
    }

    hasPendingReading = true;

    Serial.println();
    Serial.println("WYNIK POMIARU:");

    serializeJsonPretty(document, Serial);

    Serial.println();

    return true;
}


void checkRainfall() {
    const float rainfall = rain.getRainfall();
    if (isfinite(rainfall) && rainfall != lastRainfall) {
        lastRainfall = rainfall;
        Serial.printf("Opad: %.2f mm\n", rainfall);
    }
}

void runMeasurementCycle() {
    if (!measurementSensorsInitialized) {
        initializeMeasurementSensors();
        measurementSensorsInitialized = true;
    }

    if (hasPendingReading && connectWiFi()) {
        sendPendingReading();
        disconnectWiFi();
    }

    if (hasPendingReading || !performMeasurement()) {
        return;
    }

    if (connectWiFi()) {
        sendPendingReading();
        disconnectWiFi();
    } else {
        Serial.println("Brak Wi-Fi. Dane zachowane w pamieci RTC.");
    }
}

void setup() {
    Serial.begin(115200);
    delay(300);

    Serial.println();
    Serial.println("================================");
    Serial.println("ANALIZATOR DESZCZOWKI - ESP32");
    Serial.println("================================");

    pinMode(PIN_SENSOR_MODE, INPUT_PULLDOWN);
    initializeRainSensor();

    if (rtcMagic != RTC_MAGIC_VALUE) {
        rtcMagic = RTC_MAGIC_VALUE;
        hasPendingReading = false;
        memset(pendingJson, 0, sizeof(pendingJson));
    }
}

void loop() {
    const uint32_t now = millis();

    if (now - lastRainCheckMs >= RAIN_CHECK_INTERVAL_MS) {
        lastRainCheckMs = now;
        checkRainfall();
    }

    const bool enabled = digitalRead(PIN_SENSOR_MODE) == HIGH;
    if (enabled != measurementMode) {
        measurementMode = enabled;
        Serial.println(enabled
            ? "GPIO32 HIGH: wlaczam pozostale czujniki i komunikacje."
            : "GPIO32 LOW: pozostaje aktywny tylko nadzor opadu.");
        if (enabled) {
            lastMeasurementMs = 0;
        } else {
            disconnectWiFi();
            measurementSensorsInitialized = false;
        }
    }

    if (measurementMode &&
        (lastMeasurementMs == 0 || now - lastMeasurementMs >= MEASUREMENT_INTERVAL_MS)) {
        lastMeasurementMs = now;
        runMeasurementCycle();
    }

    delay(20);
}
