                      
"""Standalone console entry point for the shared Mock ESP32 sensor model."""

import time
from raspberry.ad_agent.mock_esp32 import MockESP32


def main():
    print("Starting Mock ESP32 Sensor Simulator. Press Ctrl+C to stop.")
    sensor = MockESP32()
    try:
        while True:
            sensor.update_sensors()
            sensor.print_sensor_data()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping Mock ESP32 Sensor Simulator")


if __name__ == "__main__":
    main()
