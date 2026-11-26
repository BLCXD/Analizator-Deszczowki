"""
Heartbeat sender for Raspberry Pi Agent
Handles sending periodic heartbeats to the backend to indicate device status
"""

import logging

logger = logging.getLogger("ad_agent")


class HeartbeatSender:
    def __init__(self, db, api_client):
        self.db = db
        self.api_client = api_client

    def send_heartbeat(self):
                                             
        try:
            if self.api_client.send_heartbeat():
                logger.debug("Heartbeat sent successfully")
                return True
            else:
                logger.warning("Failed to send heartbeat")
                return False

        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            return False
