

#include <Wire.h>
#include <DFRobot_ADS1115.h>
#include <DFRobot_RainfallSensor.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

static constexpr uint8_t PIN_ONEWIRE = 4;
static constexpr uint32_t INTERVAL_MS = 5000;

static constexpr float PH_V_AT_4 = 3.00f;
static constexpr float PH_V_AT_7 = 2.50f;

static constexpr float EC_V_AT_1413 = 1.00f;
static constexpr float EC_V_AT_12880 = 2.00f;

DFRobot_ADS1115 ads(&Wire);
DFRobot_RainfallSensor_I2C rain(&Wire);
OneWire oneWire(PIN_ONEWIRE);
DallasTemperature temperatureSensor(&oneWire);
uint32_t lastMeasure = 0;

float readVoltage(uint8_t channel) {

  return ads.readVoltage(channel) / 1000.0f;
}

float readPH(float voltage) {
  return 7.0f + (voltage - PH_V_AT_7) * 3.0f / (PH_V_AT_7 - PH_V_AT_4);
}

float readEC(float voltage) {
  return 1413.0f + (voltage - EC_V_AT_1413) *
      (12880.0f - 1413.0f) / (EC_V_AT_12880 - EC_V_AT_1413);
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  ads.setAddr_ADS1115(ADS1115_IIC_ADDRESS0);
  ads.init();
  ads.setGain(eGAIN_TWOTHIRDS);
  ads.setMode(eMODE_SINGLE);
  ads.setRate(eRATE_128);
  ads.setOSMode(eOSMODE_SINGLE);
  temperatureSensor.begin();
  rain.begin();
}

void loop() {
  if (millis() - lastMeasure < INTERVAL_MS) return;
  lastMeasure = millis();

  temperatureSensor.requestTemperatures();
  const float temp = temperatureSensor.getTempCByIndex(0);
  const float phVoltage = readVoltage(0);
  const float ecVoltage = readVoltage(1);
  const float turbidityVoltage = readVoltage(2);

  StaticJsonDocument<256> doc;
  if (temp != DEVICE_DISCONNECTED_C && !isnan(temp)) doc["temperature"] = temp;
  const float ph = readPH(phVoltage);
  const float ec = readEC(ecVoltage);

  if (isfinite(ph) && ph >= 0 && ph <= 14) doc["ph"] = ph;
  if (isfinite(ec) && ec >= 0 && ec <= 3000) doc["ec"] = ec;
  doc["turbidity_voltage"] = turbidityVoltage;
  doc["rainfall_mm"] = rain.getRainfall();
  doc["rainfall_1h_mm"] = rain.getRainfall(1);

  serializeJson(doc, Serial);
  Serial.println();
}
