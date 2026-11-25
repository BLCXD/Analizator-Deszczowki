"""Read the latest sensor JSON line from the ESP32 serial stream."""

import json
import serial
import time
from typing import Optional


class SerialESP32:
    def __init__(self, serial_port: str = '/dev/ttyUSB0', baudrate: int = 115200, timeout: float = 1.0):
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self._connect()
        self.data = {}

    def _connect(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=self.timeout)
            time.sleep(2)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
        except serial.SerialException as exc:
            print(f"Failed to connect to serial port {self.serial_port}: {exc}")
            self.ser = None

    def update_sensors(self):
        if not self.ser or not self.ser.is_open:
            self._connect()
            if not self.ser:
                return

        try:
            while self.ser.in_waiting:
                line = self.ser.readline().decode('utf-8').strip()
                if line:
                    parsed = json.loads(line)
                    if isinstance(parsed, dict):
                        self.data = parsed
        except ValueError as exc:
            print(f"Invalid sensor data: {exc}")
        except serial.SerialException as exc:
            print(f"Serial error: {exc}")
            self.ser = None

    def get_sensor_data(self):
        return {
            "temperature": self.data.get("temperature"),
            "ph": self.data.get("ph"),
            "ec": self.data.get("ec"),
            "turbidity": self.data.get("turbidity"),
            "turbidity_voltage": self.data.get("turbidity_voltage"),
            "rainfall_mm": self.data.get("rainfall_mm"),
            "rainfall_1h_mm": self.data.get("rainfall_1h_mm"),
        }

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
