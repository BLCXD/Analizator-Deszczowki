# Raspberry Pi Agent for Analizator Deszczówki (Deployment Version)

The Raspberry Pi agent receives ESP32 readings on a private Wi-Fi network,
stores them in its durable SQLite queue and forwards them to the AD backend.
The Pi's built-in Wi-Fi hosts ESP32; a USB LTE modem such as the planned Huawei
E3372h-153 can provide the Pi's Internet uplink. The local portal is available
at `https://baza.deszczowka.io/` from the ADE Wi-Fi network. Caddy terminates
TLS locally while dnsmasq provides a private split-horizon DNS answer.

## File Structure

```
raspberry-deploy/
├── ad_agent/                 # Raspberry Pi agent code
│   ├── api_client.py         # Backend API client
│   ├── config.py             # Environment-based configuration
│   ├── db.py                 # Local SQLite database for queuing
│   ├── heartbeat.py          # Heartbeat sender
│   ├── logger.py             # Logging setup
│   ├── main.py               # Main entry point
│   ├── measurements.py       # Measurement processing
│   ├── mock_esp32.py         # Mock ESP32 simulator
│   ├── serial_esp32.py       # Serial ESP32 interface (for real hardware)
│   └── __init__.py
└── esp32/                    # ESP32 Arduino code
    └── esp32_sensor.ino      # ESP32 sensor firmware
```

## Configuration

Do not edit `ad_agent/config.py` to add credentials. Provide these environment
variables through a root-readable environment file:

1. **Backend URL**: Set `BACKEND_URL` to your backend server (e.g., `https://api.deszczowka.io`)
2. **Device Credentials**: On first boot the Pi creates its own device ID, claim key, session key and device secret under `/var/lib/ad-agent` with mode 0600. Configure the same `DEVICE_CLAIM_KEY` in the backend secret store.
3. **Sensor Mode**: Set `USE_WIFI_SENSOR=true` for ESP32 Wi-Fi, or `USE_MOCK_SENSOR=true` for development. Leave both false to use USB serial.
4. **ESP32 local token**: Set a unique random `ESP32_LOCAL_TOKEN` (at least 32 characters). This is separate from `DEVICE_SECRET` and must also be placed in the ESP32's private `wifi_config.h`.
5. **Intervals**: Adjust `SYNC_INTERVAL` and `HEARTBEAT_INTERVAL` as needed
6. **Database Path**: Set `DB_PATH` if you want to store the database elsewhere

## Installation on Raspberry Pi

1. Copy this folder to your Raspberry Pi
2. Install required Python packages in a virtual environment:
   ```bash
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure Raspberry Pi OS Wi-Fi access point with NetworkManager:
   ```bash
   sudo ./scripts/setup-ap.sh ADE 'choose-a-private-password'
   ```
   This creates/updates only the `ad-esp32-ap` Wi-Fi profile and sets the Pi
   address to `10.42.0.1`. Install dnsmasq to resolve `baza.deszczowka.io`
   to `10.42.0.1` only for local Wi-Fi clients. This leaves public DNS unchanged.

## Run as a service

Create a dedicated service account and persistent queue directory:

```bash
sudo useradd --system --groups dialout --home-dir /var/lib/ad-agent --create-home ad-agent
sudo install -d -o ad-agent -g ad-agent /var/lib/ad-agent
sudo install -d -m 0700 /etc/ad-agent
sudo nano /etc/ad-agent/ad-agent.env
```

Add `BACKEND_URL=https://api.deszczowka.io`, `USE_WIFI_SENSOR=true`,
`ESP32_LOCAL_TOKEN`, `LOCAL_GATEWAY_HOST=10.42.0.1`, and `AD_SECURE_COOKIE=true`.
Keep the file private (`chmod 600`); never put the backend device secret in ESP32
firmware. The backend and Pi must be securely provisioned with the same claim
key before enabling account claim. Copy `/var/lib/ad-agent/claim-key` through a
secure provisioning channel to the backend as `DEVICE_CLAIM_KEY`; never send it
through the portal or public network. Set `TLS_EMAIL` and `CLOUDFLARE_API_TOKEN`
in `/etc/ad-agent/tls.env` for DNS-01 certificate issuance. Install Caddy with
its Cloudflare DNS module and enable all three units:

```bash
sudo install -m 0644 systemd/ad-agent.service /etc/systemd/system/ad-agent.service
sudo install -m 0644 systemd/ad-caddy.service /etc/systemd/system/ad-caddy.service
sudo install -m 0644 systemd/ad-dnsmasq.service /etc/systemd/system/ad-dnsmasq.service
sudo install -m 0644 caddy/Caddyfile /etc/ad-agent/Caddyfile
sudo install -m 0644 dns/dnsmasq.conf /etc/ad-agent/dnsmasq.conf
sudo systemctl daemon-reload
sudo systemctl enable --now ad-agent ad-dnsmasq ad-caddy
sudo systemctl status ad-agent ad-dnsmasq ad-caddy
```

For development, set `USE_MOCK_SENSOR=true`. This exercises the Raspberry agent
without physical ESP32 hardware. The simulation is not a replacement for sensor
calibration or field testing.

## Manual usage

### For Testing (Mock Sensor):
```bash
# Set the mock mode through the service environment file or shell environment.
export USE_MOCK_SENSOR=true
python3 ad_agent/main.py
```

### For production (ESP32 Wi-Fi):
```bash
# Set up the AP and service first, then connect the ESP32 to that network.
python3 ad_agent/main.py
```

## ESP32 Setup

Copy `esp32/wifi_config.h.example` to `esp32/wifi_config.h`, set the same AP
SSID/password and local token as the Pi, then upload `esp32/esp32_sensor.ino`
to the ESP32-DevKit. The ESP32 joins only that configured network; it does not
scan for or join other Wi-Fi networks. It retries the same pending measurement
until the Pi confirms the durable local queue accepted it. The panel reports
ESP32 freshness, latest readings, queue depth, and backend heartbeat state.

Install these Arduino libraries: `DFRobot_ADS1115`, `DFRobot_RainfallSensor`,
`DFRobot_RTU`, `OneWire`, `DallasTemperature`, and `ArduinoJson`.

Wiring assumed by the sketch: ADS1115 SDA/SCL to ESP32 GPIO 21/22 through the
BOM logic-level converter if the ADC is powered at 5 V; pH to ADS A0, EC
(through the DFR0504 isolator) to A1, turbidity to A2; DS18B20 data to GPIO 4
with a 4.7 kΩ pull-up to 3.3 V; SEN0575 on the same I2C bus with its DIP switch
set to I2C. Power/configure the ADC so every analog input stays within its
permitted input range. The ADS1115 and SEN0575 I2C addresses must not conflict.

GPIO 32 is the sensor-mode input: HIGH enables the ADS1115/DS18B20 readings
and Wi-Fi uploads every 30 minutes; LOW leaves only the rainfall monitor
running. The ESP32 stays awake in both modes so rainfall is polled every second.
Drive GPIO 32 with 3.3 V logic (the input has a pull-down). GPIO 32 is not a
power output; if the other sensors must be physically disconnected in LOW mode,
use the same selector to control a suitable external load switch for their
power rail. Keep the SEN0575 powered in both modes.

Before relying on readings, calibrate `PH_V_AT_4`, `PH_V_AT_7`,
`EC_V_AT_1413`, and `EC_V_AT_12880` from your actual reference solutions.
Turbidity is emitted as `turbidity_voltage`; its NTU conversion requires
calibration. No battery divider appears in the BOM, so the sketch does not
fabricate a battery reading. The agent and API ingest cumulative and hourly
rainfall. Tank level is not part of the measurement contract or interface.

## Notes

- The agent uses a local SQLite database to queue measurements when backend is unavailable
- Measurements are sent with retry logic
- Heartbeats are sent regularly to indicate device status
- Graceful shutdown on SIGINT/SIGTERM (Ctrl+C)
- All activities are logged to console and can be configured via LOG_LEVEL

## Environment Variables

All configuration can be overridden via environment variables:
- `AGENT_ID`: Agent identifier
- `BACKEND_URL`: Backend API URL
- `DEVICE_ID`: Device ID for authentication
- `DEVICE_SECRET`: Device secret for authentication
- `USE_MOCK_SENSOR`: "true" to use mock sensor, "false" for serial
- `USE_WIFI_SENSOR`: "true" to receive real ESP32 data over the Raspberry Pi AP
- `ESP32_LOCAL_TOKEN`: private token shared by ESP32 and local gateway (not the cloud device secret)
- `LOCAL_GATEWAY_HOST`: Pi AP address (default: `10.42.0.1`)
- `LOCAL_GATEWAY_PORT`: local panel/receiver port (default: `8081`)
- `LOGIN_HOST`: local login page bind host (default: `0.0.0.0`)
- `LOGIN_PORT`: local login page port (default: `8000`)
- `AD_DASHBOARD_URL`: dashboard URL the login page redirects to after login (default: `https://app.deszczowka.io`)
- `SERIAL_PORT`: Serial port device (default: `/dev/ttyUSB0`)
- `SYNC_INTERVAL`: Seconds between sensor readings (default: 30)
- `HEARTBEAT_INTERVAL`: Seconds between heartbeats (default: 60)
- `MAX_RETRY_ATTEMPTS`: Max retries for failed operations (default: 3)
- `RETRY_DELAY`: Seconds between retries (default: 5)
- `DB_PATH`: Path to SQLite database (default: `./data/agent.db`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
