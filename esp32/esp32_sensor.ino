#include <Arduino.h>
#include <Wire.h>
#include <DFRobot_ADS1115.h>
#include <DFRobot_RainfallSensor.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <esp_system.h>
#include <esp_sleep.h>
#include <driver/gpio.h>
#include <math.h>

#include "wifi_config.h"

// ===================== CONFIG =====================

// Czas deep sleep (minuty) - po tym czasie ESP32 budzi sie i mierzy
static constexpr uint32_t SLEEP_INTERVAL_MIN = 30;
static constexpr uint64_t SLEEP_INTERVAL_US =
    (uint64_t)SLEEP_INTERVAL_MIN * 60ULL * 1000000ULL;

// Piny
static constexpr uint8_t PIN_ONEWIRE = 4;
static constexpr uint8_t PIN_SDA = 21;
static constexpr uint8_t PIN_SCL = 22;
static constexpr gpio_num_t PIN_SENSOR_POWER = GPIO_NUM_32; // HIGH = czujniki zasilane (MOSFET)

// Czas na ustabilizowanie zasilania czujnikow po ustawieniu GPIO32 na HIGH (ms)
static constexpr uint32_t POWER_STABILIZE_MS = 2000;

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

// Pamiec RTC przezywa deep sleep
RTC_DATA_ATTR uint32_t rtcMagic = 0;
RTC_DATA_ATTR bool hasPendingReading = false;
RTC_DATA_ATTR char pendingJson[512] = {0};

// ===================== OBIEKTY =====================

DFRobot_ADS1115 ads(&Wire);
DFRobot_RainfallSensor_I2C rain(&Wire);
OneWire oneWire(PIN_ONEWIRE);
DallasTemperature temperatureSensor(&oneWire);

bool rainSensorReady = false;
uint8_t adsAddress = 0;

// ===================== POMOCNICZE =====================

bool isI2CDevicePresent(uint8_t address) {
    Wire.beginTransmission(address);
    return (Wire.endTransmission() == 0);
}

// Odczyt napięcia ADS1115 (V)
float readVoltage(uint8_t channel) {
    return ads.readVoltage(channel) / 1000.0f;
}

float readPH(float voltage) {
    return 7.0f +
           (voltage - PH_V_AT_7) * 3.0f /
           (PH_V_AT_7 - PH_V_AT_4);
}

float readEC(float voltage) {
    return 1413.0f +
           (voltage - EC_V_AT_1413) *
           (12880.0f - 1413.0f) /
           (EC_V_AT_12880 - EC_V_AT_1413);
}

float readTurbidityNTU(float voltage) {
    return -1120.4f * voltage * voltage +
           5742.3f * voltage -
           4353.8f;
}

// MAC z eFuse - dziala takze, gdy Wi-Fi jest wylaczone
void getSensorId(char* output) {
    const uint64_t efuseMac = ESP.getEfuseMac();
    uint8_t mac[6];
    for (uint8_t i = 0; i < 6; i++) {
        mac[i] = (efuseMac >> (8 * i)) & 0xFF;
    }
    snprintf(output, 18, "%02X:%02X:%02X:%02X:%02X:%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

// UUID v4
void generateMeasurementId(char* output) {
    uint8_t bytes[16];

    for (uint8_t i = 0; i < 16; i += 4) {
        uint32_t randomValue = esp_random();
        memcpy(&bytes[i], &randomValue, 4);
    }

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

// Linia w Serial Monitor: wartość + informacja, czy trafi do JSON
void logReading(const char* name, float value, const char* unit, bool accepted, const char* reason) {
    if (accepted) {
        Serial.printf("  %-16s %10.3f %-6s [OK -> JSON]\n", name, value, unit);
    } else {
        Serial.printf("  %-16s %10.3f %-6s [POMINIETE: %s]\n", name, value, unit, reason);
    }
}

// ===================== ZASILANIE CZUJNIKOW (GPIO32) =====================

// HIGH + zwolnienie "hold" po deep sleep. Najpierw ustawiamy poziom, potem zwalniamy hold,
// dzieki temu pin przechodzi prosto z LOW na HIGH bez chwilowego stanu plywajacego.
void powerSensorsOn() {
    pinMode(PIN_SENSOR_POWER, OUTPUT);
    digitalWrite(PIN_SENSOR_POWER, HIGH);
    gpio_hold_dis(PIN_SENSOR_POWER);
    gpio_deep_sleep_hold_dis();

    Serial.printf("GPIO%d: HIGH - zasilanie czujnikow wlaczone. Czekam %lu ms na stabilizacje...\n",
                  (int)PIN_SENSOR_POWER, (unsigned long)POWER_STABILIZE_MS);
    delay(POWER_STABILIZE_MS);
}

// LOW + zatrzask (hold), zeby pin zostal LOW przez caly deep sleep, po czym deep sleep
void goToDeepSleep() {
    Serial.println();
    Serial.printf("GPIO%d: LOW - zasilanie czujnikow wylaczone.\n", (int)PIN_SENSOR_POWER);
    Serial.printf("Deep sleep na %lu min...\n", (unsigned long)SLEEP_INTERVAL_MIN);
    Serial.flush();

    digitalWrite(PIN_SENSOR_POWER, LOW);
    gpio_hold_en(PIN_SENSOR_POWER);
    gpio_deep_sleep_hold_en();

    esp_sleep_enable_timer_wakeup(SLEEP_INTERVAL_US);
    esp_deep_sleep_start();
}

// ===================== INICJALIZACJA CZUJNIKOW =====================

void initializeRainSensor() {
    Wire.begin(PIN_SDA, PIN_SCL);

    for (uint8_t attempt = 1; attempt <= 3 && !rainSensorReady; attempt++) {
        rainSensorReady = rain.begin();
        if (!rainSensorReady) {
            delay(500);
        }
    }

    Serial.println(rainSensorReady ? "SEN0575: polaczono."
                                   : "SEN0575: BLAD inicjalizacji.");
}

void initializeMeasurementSensors() {
    // ADS1115 - automatyczne wykrycie adresu 0x48 / 0x49
    adsAddress = 0;
    if (isI2CDevicePresent(ADS1115_IIC_ADDRESS0)) {
        adsAddress = ADS1115_IIC_ADDRESS0;
    } else if (isI2CDevicePresent(ADS1115_IIC_ADDRESS1)) {
        adsAddress = ADS1115_IIC_ADDRESS1;
    }

    if (adsAddress != 0) {
        ads.setAddr_ADS1115(adsAddress);
        ads.init();
        ads.setGain(eGAIN_TWOTHIRDS);
        ads.setMode(eMODE_SINGLE);
        ads.setRate(eRATE_128);
        ads.setOSMode(eOSMODE_SINGLE);
        Serial.printf("ADS1115: wykryto na 0x%02X\n", adsAddress);
    } else {
        Serial.println("ADS1115: BLAD - brak odpowiedzi na 0x48 i 0x49.");
    }

    // Temperatura
    temperatureSensor.begin();
    Serial.printf("DS18B20: wykryto %u czujnik(ow)\n", temperatureSensor.getDeviceCount());
}

// ===================== WI-FI =====================

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

void disconnectWiFi() {
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    delay(100);
}

// ===================== WYSYLKA =====================

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

    Serial.println("JSON do wyslania:");
    Serial.println(pendingJson);

    bool success = false;

    for (uint8_t attempt = 1; attempt <= HTTP_MAX_ATTEMPTS; attempt++) {
        Serial.printf("Wysylanie danych - proba %u/%u\n", attempt, HTTP_MAX_ATTEMPTS);

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

// ===================== POMIAR =====================

bool performMeasurement() {
    Serial.println();
    Serial.println("================================");
    Serial.println("ROZPOCZYNAM POMIAR AD");
    Serial.println("================================");

    StaticJsonDocument<384> document;

    char sensorId[18];
    getSensorId(sensorId);
    document["sensor_id"] = sensorId;

    char measurementId[37];
    generateMeasurementId(measurementId);
    document["measurement_id"] = measurementId;

    // ---- Temperatura ----
    float temp = NAN;
    if (temperatureSensor.getDeviceCount() > 0) {
        temperatureSensor.requestTemperatures();
        temp = temperatureSensor.getTempCByIndex(0);
    }

    if (isnan(temp) || temp == DEVICE_DISCONNECTED_C) {
        logReading("Temperatura", temp, "C", false, "brak odczytu / odlaczony");
    } else if (temp == 85.0f) {
        logReading("Temperatura", temp, "C", false, "85.0 = wartosc startowa DS18B20");
    } else {
        logReading("Temperatura", temp, "C", true, "");
        document["temperature"] = temp;
    }

    // ---- Czujniki analogowe (ADS1115) ----
    if (adsAddress != 0) {
        const float phVoltage = readVoltage(0);
        const float ecVoltage = readVoltage(1);
        const float turbidityVoltage = readVoltage(2);

        const float ph = readPH(phVoltage);
        const float ec = readEC(ecVoltage);
        const float turbidityNtu = readTurbidityNTU(turbidityVoltage);

        Serial.printf("  Napiecia ADS: A0(pH)=%.4f V | A1(EC)=%.4f V | A2(Metnosc)=%.4f V\n",
                      phVoltage, ecVoltage, turbidityVoltage);

        const bool phOk = SENSOR_CALIBRATION_COMPLETE && isfinite(ph) && ph >= 0 && ph <= 14;
        logReading("pH", ph, "", phOk,
                   SENSOR_CALIBRATION_COMPLETE ? "poza zakresem 0..14" : "brak kalibracji");
        if (phOk) document["ph"] = ph;

        const bool ecOk = SENSOR_CALIBRATION_COMPLETE && isfinite(ec) && ec >= 0 && ec <= 3000;
        logReading("EC", ec, "uS/cm", ecOk,
                   SENSOR_CALIBRATION_COMPLETE ? "poza zakresem 0..3000" : "brak kalibracji");
        if (ecOk) document["ec"] = ec;

        const bool turbOk = isfinite(turbidityNtu) && turbidityNtu >= 0 && turbidityNtu <= 3000;
        logReading("Metnosc", turbidityNtu, "NTU", turbOk, "poza zakresem 0..3000");
        if (turbOk) document["turbidity_ntu"] = turbidityNtu;
    } else {
        Serial.println("  ADS1115 niedostepny - pomijam pH, EC i metnosc.");
    }

    // ---- Opad ----
    if (rainSensorReady) {
        const float rainfall = rain.getRainfall();
        const float rainfall1h = rain.getRainfall(1);

        const bool rainOk = isfinite(rainfall) && rainfall >= 0;
        logReading("Opad calkowity", rainfall, "mm", rainOk, "nieprawidlowa wartosc");
        if (rainOk) document["rainfall_mm"] = rainfall;

        const bool rain1hOk = isfinite(rainfall1h) && rainfall1h >= 0;
        logReading("Opad 1h", rainfall1h, "mm", rain1hOk, "nieprawidlowa wartosc");
        if (rain1hOk) document["rainfall_1h_mm"] = rainfall1h;
    } else {
        Serial.println("  SEN0575 niedostepny - pomijam opad.");
    }

    // ---- Zapis do RTC ----
    const size_t written =
        serializeJson(document, pendingJson, sizeof(pendingJson));

    if (written == 0 || document.overflowed()) {
        Serial.println("Blad zapisu JSON!");
        memset(pendingJson, 0, sizeof(pendingJson));
        return false;
    }

    hasPendingReading = true;

    Serial.println();
    Serial.println("WYNIK POMIARU (JSON):");
    serializeJsonPretty(document, Serial);
    Serial.println();

    return true;
}

void runMeasurementCycle() {
    initializeMeasurementSensors();

    if (hasPendingReading) {
        Serial.println("Poprzedni pomiar czeka na wyslanie - probuje wyslac.");
        if (connectWiFi()) {
            sendPendingReading();
            disconnectWiFi();
        }
    }

    if (hasPendingReading) {
        Serial.println("Pomiar nadal czeka na wyslanie - pomijam nowy pomiar.");
        return;
    }

    if (!performMeasurement()) {
        return;
    }

    if (connectWiFi()) {
        sendPendingReading();
        disconnectWiFi();
    } else {
        Serial.println("Brak Wi-Fi. Dane zachowane w pamieci RTC.");
    }
}

// ===================== SETUP / LOOP =====================
// Kazde wybudzenie z deep sleep = reset, wiec caly cykl dzieje sie w setup().

void setup() {
    Serial.begin(115200);
    delay(300);

    Serial.println();
    Serial.println("================================");
    Serial.println("ANALIZATOR DESZCZOWKI - ESP32");
    Serial.println("================================");

    const esp_sleep_wakeup_cause_t wakeCause = esp_sleep_get_wakeup_cause();
    Serial.println(wakeCause == ESP_SLEEP_WAKEUP_TIMER
                       ? "Start: wybudzenie z deep sleep (timer)."
                       : "Start: wlaczenie zasilania / reset.");

    if (rtcMagic != RTC_MAGIC_VALUE) {
        rtcMagic = RTC_MAGIC_VALUE;
        hasPendingReading = false;
        memset(pendingJson, 0, sizeof(pendingJson));
    }

    // 1. GPIO32 -> HIGH, odczekanie 2 s
    powerSensorsOn();

    // 2. I2C + czujnik opadu
    initializeRainSensor();

    // 3. Pomiar + wysylka
    runMeasurementCycle();

    // 4. GPIO32 -> LOW, deep sleep
    goToDeepSleep();
}

void loop() {
    // Nigdy nie wykonywane - po pomiarze ESP32 idzie spac w setup()
}
//#define AD_LOCAL_TOKEN "4635bee91a9399877f6b25ec2c662514c08dd3bf71759f96a3b98d4a5093ffc8"