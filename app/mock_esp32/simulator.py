                      
"""Mock ESP32 file-output adapter using the shared sensor model."""

import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from raspberry.ad_agent.mock_esp32 import MockESP32 as SensorModel


class MockESP32:
    def __init__(self, device_id: str, output_dir: str = "/tmp/esp32_out"):
        self.device_id = device_id
        self.output_dir = output_dir
        self.sensor = SensorModel()
        os.makedirs(self.output_dir, mode=0o750, exist_ok=True)

    def generate_sensor_data(self) -> Dict[str, Any]:
        self.sensor.update_sensors()
        reading = self.sensor.get_sensor_data()
        return {
            "measurement_id": str(uuid.uuid4()),
            "device_id": self.device_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "water_quality_turbidity": reading["turbidity"],
            "ec": reading["ec"],
            "water_quality_ph": reading["ph"],
            "temperature": reading["temperature"],
        }

    def write_data(self, data: Dict[str, Any]) -> bool:
        path = Path(self.output_dir) / f"{data['measurement_id']}.json"
        try:
            path.write_text(json.dumps(data), encoding="utf-8")
        except OSError as error:
            print(f"Could not write simulated measurement: {error}")
            return False
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Wrote {path.name}")
        return True

    def run(self, interval: float = 5.0):
        print(f"Starting Mock ESP32 for {self.device_id}; writing every {interval:g}s")
        try:
            while True:
                self.write_data(self.generate_sensor_data())
                time.sleep(interval)
        except KeyboardInterrupt:
            print("Stopping Mock ESP32 simulator")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Mock ESP32 file-output simulator")
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--output-dir", default="/tmp/esp32_out")
    parser.add_argument("--interval", type=float, default=5.0)
    args = parser.parse_args()
    MockESP32(args.device_id, args.output_dir).run(args.interval)


if __name__ == "__main__":
    main()
