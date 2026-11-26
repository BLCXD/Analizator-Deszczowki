"""
Measurement processing module for Raspberry Pi Agent
Handles reading from the queue and sending to backend with retry logic
"""

import logging

logger = logging.getLogger("ad_agent")


class MeasurementProcessor:
    def __init__(self, db, api_client):
        self.db = db
        self.api_client = api_client

    def process_queue(self):
                                                        
        measurements = self.db.get_unsent_measurements(limit=50)

        if not measurements:
            logger.debug("No unsent measurements in queue")
            return

        logger.info(f"Processing {len(measurements)} measurements from queue")

        successful_ids = []
        failed_ids = []

        for measurement in measurements:
            try:
                if self.api_client.send_measurement(measurement):
                    successful_ids.append(measurement['id'])
                    logger.debug(f"Sent measurement {measurement['measurement_id']}")
                else:
                    failed_ids.append(measurement['id'])
                    logger.warning(f"Failed to send measurement {measurement['measurement_id']}")

            except Exception as e:
                logger.error(f"Error processing measurement {measurement['id']}: {e}")
                failed_ids.append(measurement['id'])

        if successful_ids:
            self.db.mark_as_sent(successful_ids)
            if hasattr(self, "on_sync"):
                self.on_sync()
            logger.info(f"Successfully sent {len(successful_ids)} measurements")

        if failed_ids:
            self.db.increment_retry_count(failed_ids)
            logger.warning(f"Failed to send {len(failed_ids)} measurements, will retry later")

        stats = self.db.get_stats()
        if stats:
            logger.debug(f"Queue stats: {stats['unsent']} unsent, {stats['sent']} sent")
