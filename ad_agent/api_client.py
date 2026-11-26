"""
API client for communicating with the FastAPI backend
"""

import requests
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("ad_agent")


class ADAPIClient:
    def __init__(self, backend_url: str, device_id: str, device_secret: str):
        if not device_id or not device_secret:
            raise ValueError("DEVICE_ID and DEVICE_SECRET are required")
        self.backend_url = backend_url.rstrip('/')
        self.device_id = device_id
        self.device_secret = device_secret
        self.session = requests.Session()
        self.device_token = None

    def _auth_headers(self) -> Dict[str, str]:
        if self.device_token is None:
            self.device_token = self._get_device_token()
        return {"Authorization": f"Bearer {self.device_token}"}

    def _post_authenticated(self, url: str, **kwargs):
        response = self.session.post(url, headers=self._auth_headers(), **kwargs)
        if response.status_code == 401:
            self.device_token = None
            response = self.session.post(url, headers=self._auth_headers(), **kwargs)
        return response

    def _get_device_token(self) -> str:
                                                       
        try:
            response = self.session.post(
                f"{self.backend_url}/api/v1/auth/device/login",
                json={
                    "device_id": self.device_id,
                    "device_secret": self.device_secret
                },
                timeout=10
            )

            if response.status_code == 200:
                token_data = response.json()
                return token_data.get("access_token")
            else:
                logger.error(f"Device authentication failed with HTTP {response.status_code}")
                raise Exception(f"Device authentication failed: {response.status_code}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to auth endpoint: {e}")
            raise

    def send_measurement(self, measurement: Dict[str, Any]) -> bool:
                                                      
        try:
            api_measurement = {
                "device_id": self.device_id,
                "measurement_id": measurement.get("measurement_id"),
                "measurement_time": measurement.get("timestamp"),
                "water_quality_turbidity": measurement.get("water_quality_turbidity"),
                "ec": measurement.get("ec"),
                "water_quality_ph": measurement.get("water_quality_ph"),
                "temperature": measurement.get("temperature"),
                "humidity": measurement.get("humidity"),
                "rainfall_mm": measurement.get("rainfall_mm"),
                "rainfall_1h_mm": measurement.get("rainfall_1h_mm"),
                "raw_data": measurement.get("raw_data")
            }

            api_measurement = {k: v for k, v in api_measurement.items() if v is not None}

            response = self._post_authenticated(
                f"{self.backend_url}/api/v1/measurements/",
                json=api_measurement,
                timeout=10
            )

            if response.status_code in [200, 201]:
                logger.debug(f"Measurement sent successfully: {measurement.get('measurement_id')}")
                return True
            else:
                logger.error(f"Failed to send measurement with HTTP {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending measurement: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending measurement: {e}")
            return False

    def send_heartbeat(self) -> bool:
                                                             
        try:
            response = self._post_authenticated(
                f"{self.backend_url}/api/v1/devices/{self.device_id}/heartbeat",
                timeout=10
            )

            if response.status_code == 200:
                logger.debug("Heartbeat sent successfully")
                return True
            else:
                logger.error(f"Heartbeat failed with HTTP {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending heartbeat: {e}")
            return False

    def get_device_info(self) -> Optional[Dict[str, Any]]:
                                                     
        try:
            response = self.session.get(
                f"{self.backend_url}/api/v1/devices/{self.device_id}",
                headers=self._auth_headers(),
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get device info: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting device info: {e}")
            return None
