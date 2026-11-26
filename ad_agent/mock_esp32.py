                      
"""
Mock ESP32 Sensor Simulator
Generates realistic sensor data for rainwater monitoring.
"""

import time
import random
from datetime import datetime


class MockESP32:
    def __init__(self):
        self.temperature = 20.0
        self.ph = 7.0
        self.ec = 850.0
        self.turbidity = 2.0

        self.temp_noise = 0.1
        self.ph_noise = 0.02
        self.ec_noise = 20.0
        self.turbidity_noise = 0.08

        self.temp_drift = 0.0
        self.ph_drift = 0.0
        self.ec_drift = 0.0
        self.turbidity_drift = 0.0

    def _random_walk(self, current, noise, drift=0.0, min_val=None, max_val=None):
                                                              
        change = random.uniform(-noise, noise) + drift
        new_val = current + change

        if min_val is not None:
            new_val = max(new_val, min_val)
        if max_val is not None:
            new_val = min(new_val, max_val)

        return new_val

    def update_sensors(self):
                                                                     
        self.temperature = self._random_walk(
            self.temperature,
            self.temp_noise,
            self.temp_drift,
            min_val=10.0,
            max_val=35.0
        )
        self.temp_drift += random.uniform(-0.001, 0.001)

        self.ph = self._random_walk(
            self.ph,
            self.ph_noise,
            self.ph_drift,
            min_val=5.5,
            max_val=9.0
        )
        self.ph_drift += random.uniform(-0.0005, 0.0005)

        self.ec = self._random_walk(
            self.ec,
            self.ec_noise,
            self.ec_drift,
            min_val=0.0,
            max_val=3000.0
        )
        self.ec_drift += random.uniform(-0.0001, 0.0001)

        self.turbidity = self._random_walk(
            self.turbidity,
            self.turbidity_noise,
            self.turbidity_drift,
            min_val=0.0,
            max_val=1000.0,
        )
        self.turbidity_drift += random.uniform(-0.0002, 0.0002)

    def get_sensor_data(self):
                                                            
        return {
            "temperature": round(self.temperature, 2),
            "ph": round(self.ph, 2),
            "ec": round(self.ec, 1),
            "turbidity": round(self.turbidity, 2)
        }

    def print_sensor_data(self):
                                                  
        data = self.get_sensor_data()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"Temp: {data['temperature']:5.1f}°C | "
              f"pH: {data['ph']:4.2f} | "
              f"EC: {data['ec']:6.1f} µS/cm | "
              f"Turbidity: {data['turbidity']:5.2f} NTU")


def main():
                              
    print("Starting Mock ESP32 Sensor Simulator")
    print("Press Ctrl+C to stop")

    esp32 = MockESP32()

    try:
        while True:
            esp32.update_sensors()
            esp32.print_sensor_data()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping Mock ESP32 Simulator")


if __name__ == "__main__":
    main()
