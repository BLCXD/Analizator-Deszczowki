"""
Main entry point for the Raspberry Pi Agent
Handles communication between ESP32 (serial or mock) and FastAPI backend
"""

import time
import threading
import signal
import sys
import os
import uuid
import json
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from logger import setup_logger
from db import MeasurementQueueDB
from api_client import ADAPIClient
from measurements import MeasurementProcessor
from heartbeat import HeartbeatSender
from local_gateway import LocalGatewayServer
from login_server import LoginServer

USE_MOCK = os.getenv("USE_MOCK_SENSOR", "false").lower() == "true"
USE_WIFI = os.getenv("USE_WIFI_SENSOR", "false").lower() == "true"
if USE_MOCK:
    from mock_esp32 import MockESP32 as ESP32Interface
else:
    from serial_esp32 import SerialESP32 as ESP32Interface

logger = setup_logger("ad_agent", LOG_LEVEL)


class RaspberryPiAgent:
    def __init__(self):
        self.running = False
        self.device_id = DEVICE_ID
        self.device_secret_path = os.getenv("DEVICE_SECRET_PATH", "/var/lib/ad-agent/device-secret")
        session_secret_path = os.getenv("AD_LOGIN_SESSION_SECRET_PATH", "/var/lib/ad-agent/session-key")
        try:
            with open(session_secret_path, encoding="utf-8") as secret_file:
                session_secret = secret_file.read().strip()
        except OSError:
            session_secret = uuid.uuid4().hex + uuid.uuid4().hex
            os.makedirs(os.path.dirname(session_secret_path), exist_ok=True)
            with open(session_secret_path, "x", encoding="utf-8") as secret_file:
                secret_file.write(session_secret)
            os.chmod(session_secret_path, 0o600)
        self.db = MeasurementQueueDB(DB_PATH)
        # A random persistent ID lets the cloud bind the first claim to this Pi.
        if not self.device_id:
            id_path = os.getenv("DEVICE_ID_PATH", "/var/lib/ad-agent/device-id")
            os.makedirs(os.path.dirname(id_path), exist_ok=True)
            try:
                with open(id_path, encoding="utf-8") as id_file:
                    self.device_id = id_file.read().strip()
            except OSError:
                self.device_id = str(uuid.uuid4())
                with open(id_path, "x", encoding="utf-8") as id_file:
                    id_file.write(self.device_id + "\n")

        # Local user login page (port 8000). Independent of device pairing — only
        # needs the backend URL — so it is reachable even before the device is
        # paired and after a reboot while credentials are being set up.
        self.api_client = None
        self.measurement_processor = None
        self.heartbeat_sender = None
        self.local_gateway = None
        self.esp32 = None
        self.backend_connected: bool | None = None

        configured_secret = DEVICE_SECRET
        if not configured_secret:
            try:
                with open(self.device_secret_path, encoding="utf-8") as secret_file:
                    configured_secret = secret_file.read().strip()
            except OSError:
                pass
        if not configured_secret:
            logger.warning(
                "Device credentials are not configured; login is available on port %d, "
                "measurement forwarding is disabled until the device is paired",
                LOGIN_PORT,
            )
        else:
            self.api_client = ADAPIClient(BACKEND_URL, self.device_id, configured_secret)
            self.measurement_processor = MeasurementProcessor(self.db, self.api_client)
            self.heartbeat_sender = HeartbeatSender(self.db, self.api_client)
            if USE_WIFI:
                if USE_MOCK:
                    raise ValueError("USE_WIFI_SENSOR and USE_MOCK_SENSOR cannot both be enabled")
                self.local_gateway = LocalGatewayServer(
                    self.db, self.device_id, os.getenv("ESP32_LOCAL_TOKEN", ""),
                    os.getenv("LOCAL_GATEWAY_HOST", "10.42.0.1"),
                    int(os.getenv("LOCAL_GATEWAY_PORT", "8081")),
                )
                self.measurement_processor.on_sync = lambda: setattr(self.local_gateway, "last_sync", datetime.utcnow().isoformat())
                logger.info("Using ESP32 Wi-Fi gateway")
            elif USE_MOCK:
                self.esp32 = ESP32Interface()
                logger.info("Using Mock ESP32 sensor interface")
            else:
                serial_port = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
                self.esp32 = ESP32Interface(serial_port=serial_port)
                logger.info(f"Using Serial ESP32 sensor interface on {serial_port}")

        self.login_server = LoginServer(
            backend_url=BACKEND_URL,
            host=LOGIN_HOST,
            port=LOGIN_PORT,
            session_secret=session_secret,
            device_id=self.device_id,
            device_secret_path=self.device_secret_path,
            status_provider=self._local_status,
        )
        if self.local_gateway:
            self.local_gateway.status = self.login_server.status_provider

        self.sync_thread = None
        self.heartbeat_thread = None

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
                                                
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()

    def start(self):

        logger.info("Starting Raspberry Pi Agent for Analizator Deszczówki")
        logger.info(f"Agent ID: {AGENT_ID}")
        logger.info(f"Backend URL: {BACKEND_URL}")
        logger.info(f"Device ID: {self.device_id}")

        # Start the local login page first — it is always available so users can
        # log in even before the device is paired or while LTE is down.
        try:
            self.login_server.start()
        except Exception as exc:
            logger.error("Login server failed to start on port %d: %s", LOGIN_PORT, exc)

        if self.api_client is None:
            logger.warning("Device is not paired; measurement forwarding and local panel are disabled.")
            self.running = True
            self.sync_thread = None
            self.heartbeat_thread = None
            logger.info("Agent started successfully (login page only)")
            return True

        backend_connected = self._verify_device()
        self.backend_connected = backend_connected
        if self.local_gateway:
            self.local_gateway.set_backend_connected(backend_connected)
        if not backend_connected:
            logger.warning("Backend is unavailable; measurements will be queued locally until it recovers")

        self.running = True
        if self.local_gateway:
            self.local_gateway.start()

        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()

        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()

        logger.info("Agent started successfully")
        return True

    def stop(self):

        logger.info("Stopping Raspberry Pi Agent...")
        self.running = False

        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
        if self.local_gateway:
            self.local_gateway.close()
        if self.login_server:
            self.login_server.close()

        if self.esp32 is not None and hasattr(self.esp32, 'close'):
            self.esp32.close()

        logger.info("Agent stopped")

    def _verify_device(self):
                                                          
        try:
            token = self.api_client._get_device_token()
            logger.info("Device verification successful")
            return True
        except Exception as e:
            logger.error(f"Device verification failed: {e}")
            return False

    def _local_status(self):
        now = datetime.now(timezone.utc).isoformat()
        if self.local_gateway:
            status = self.local_gateway.status()
        else:
            status = {
                "device_id": self.device_id,
                "agent_version": "1.0.0",
                "firmware_version": None,
                "last_sync": None,
                "queued_measurements": self.db.get_unsent_count(),
                "sensors": [],
            }
        status["backend_connected"] = self.backend_connected
        status["internet_connected"] = self.backend_connected
        status["lte_connected"] = self.backend_connected is True
        status["updated_at"] = now
        return status

    def _sync_loop(self):
                                       
        logger.info("Starting sync loop")
        while self.running:
            try:
                if USE_WIFI:
                    self.measurement_processor.process_queue()
                    time.sleep(SYNC_INTERVAL)
                    continue

                self.esp32.update_sensors()

                sensor_data = self.esp32.get_sensor_data()
                measurement = {
                    'measurement_id': str(uuid.uuid4()),
                    'device_id': self.device_id,
                    'water_quality_turbidity': sensor_data['turbidity'],
                    'ec': sensor_data['ec'],
                    'water_quality_ph': sensor_data['ph'],
                    'temperature': sensor_data['temperature'],
                    'humidity': None,
                    'rainfall_mm': sensor_data.get('rainfall_mm'),
                    'rainfall_1h_mm': sensor_data.get('rainfall_1h_mm'),
                    'raw_data': json.dumps({
                        'temperature': sensor_data['temperature'],
                        'ph': sensor_data['ph'],
                        'ec': sensor_data['ec'],
                        'turbidity': sensor_data['turbidity'],
                        'turbidity_voltage': sensor_data.get('turbidity_voltage'),
                        'rainfall_mm': sensor_data.get('rainfall_mm'),
                        'rainfall_1h_mm': sensor_data.get('rainfall_1h_mm')
                    }),
                    'timestamp': datetime.utcnow().isoformat()
                }

                if self.db.add_measurement(measurement):
                    logger.debug(f"Added measurement to queue: {measurement['measurement_id']}")
                else:
                    logger.warning("Failed to add measurement to queue (duplicate?)")

                self.measurement_processor.process_queue()

                time.sleep(SYNC_INTERVAL)
            except Exception as e:
                logger.error(f"Error in sync loop: {e}")
                time.sleep(5)

    def _heartbeat_loop(self):
                                                  
        logger.info("Starting heartbeat loop")
        while self.running:
            try:
                connected = self.heartbeat_sender.send_heartbeat()
                self.backend_connected = connected
                if self.local_gateway:
                    self.local_gateway.set_backend_connected(connected)

                time.sleep(HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                time.sleep(5)


if __name__ == "__main__":
    agent = RaspberryPiAgent()
    if agent.start():
        try:
            while agent.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            agent.stop()
    else:
        logger.error("Failed to start agent")
        sys.exit(1)
