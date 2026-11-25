"""
Configuration for Raspberry Pi Agent
"""

import os
AGENT_ID = os.getenv("AGENT_ID", "raspberry-pi-001")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DEVICE_ID = os.getenv("DEVICE_ID", "")
DEVICE_SECRET = os.getenv("DEVICE_SECRET", "")

SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "30"))
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "60"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))

USE_MOCK_SENSOR = os.getenv("USE_MOCK_SENSOR", "false").lower() == "true"
SERIAL_PORT = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
USE_WIFI_SENSOR = os.getenv("USE_WIFI_SENSOR", "false").lower() == "true"
ESP32_LOCAL_TOKEN = os.getenv("ESP32_LOCAL_TOKEN", "")
LOCAL_GATEWAY_HOST = os.getenv("LOCAL_GATEWAY_HOST", "10.42.0.1")
LOCAL_GATEWAY_PORT = int(os.getenv("LOCAL_GATEWAY_PORT", "8081"))

# Local user login page that proxies to the AD backend API and redirects to the dashboard.
LOGIN_HOST = os.getenv("LOGIN_HOST", "127.0.0.1")
LOGIN_PORT = int(os.getenv("LOGIN_PORT", "8000"))

DB_PATH = os.getenv("DB_PATH", "./data/agent.db")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
