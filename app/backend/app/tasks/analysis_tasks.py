import logging
from datetime import datetime, timedelta

from backend.app.tasks.celery_config import celery_app
from backend.app.db.session import SessionLocal
from backend.app.services.measurement import get_measurements_since_timestamp
from backend.app.services.device import get_device_by_id
from backend.app.analysis.service import analysis_service

logger = logging.getLogger(__name__)


def _get_measurement_data(db, device_id, hours):
    since = datetime.utcnow() - timedelta(hours=hours)
    measurements = get_measurements_since_timestamp(db=db, device_id=device_id, since=since)
    return [
        {
            "measurement_time": measurement.measurement_time.isoformat() if measurement.measurement_time else None,
            "device_id": measurement.device_id,
            "water_quality_ph": measurement.water_quality_ph,
            "water_quality_turbidity": measurement.water_quality_turbidity,
            "temperature": measurement.temperature,
            "humidity": measurement.humidity,
        }
        for measurement in measurements
    ]


@celery_app.task
def analyze_device_trends(device_id: str, user_id: int, hours: int = 24):
    db = SessionLocal()
    try:
        device = get_device_by_id(db, device_id)
        if not device:
            logger.warning(f"Device {device_id} not found")
            return {"error": "Device not found"}

        if device.user_id != user_id:
            logger.warning(f"User {user_id} not authorized for device {device_id}")
            return {"error": "Not authorized"}

        measurement_dicts = _get_measurement_data(db, device.id, hours)

        if not measurement_dicts:
            logger.info(f"No measurements found for device {device_id} in last {hours} hours")
            return {"info": "No measurements found"}

        trends = analysis_service.analyze_trends(measurement_dicts)

        logger.info(f"Completed trend analysis for device {device_id}")
        return {
            "device_id": device_id,
            "analysis_period_hours": hours,
            "measurement_count": len(measurement_dicts),
            "trends": trends,
            "analyzed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error analyzing trends for device {device_id}: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task
def detect_device_anomalies(device_id: str, user_id: int, hours: int = 24):
    db = SessionLocal()
    try:
        device = get_device_by_id(db, device_id)
        if not device:
            logger.warning(f"Device {device_id} not found")
            return {"error": "Device not found"}

        if device.user_id != user_id:
            logger.warning(f"User {user_id} not authorized for device {device_id}")
            return {"error": "Not authorized"}

        measurement_dicts = _get_measurement_data(db, device.id, hours)

        if len(measurement_dicts) < 10:
            logger.info(f"Insufficient measurements for anomaly detection on device {device_id}")
            return {"info": "Insufficient data for anomaly detection"}

        anomalies = analysis_service.detect_anomalies(measurement_dicts)

        logger.info(f"Completed anomaly detection for device {device_id}")
        return {
            "device_id": device_id,
            "analysis_period_hours": hours,
            "measurement_count": len(measurement_dicts),
            "anomaly_count": len(anomalies),
            "anomalies": anomalies[:10] if anomalies else [],
            "analyzed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error detecting anomalies for device {device_id}: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task
def predict_device_values(device_id: str, user_id: int, hours: int = 24, steps_ahead: int = 5):
    db = SessionLocal()
    try:
        device = get_device_by_id(db, device_id)
        if not device:
            logger.warning(f"Device {device_id} not found")
            return {"error": "Device not found"}

        if device.user_id != user_id:
            logger.warning(f"User {user_id} not authorized for device {device_id}")
            return {"error": "Not authorized"}

        measurement_dicts = _get_measurement_data(db, device.id, hours)

        if len(measurement_dicts) < 5:
            logger.info(f"Insufficient measurements for prediction on device {device_id}")
            return {"info": "Insufficient data for prediction"}

        predictions = analysis_service.predict_next_values(measurement_dicts, steps_ahead)

        logger.info(f"Completed prediction analysis for device {device_id}")
        return {
            "device_id": device_id,
            "historical_period_hours": hours,
            "measurement_count": len(measurement_dicts),
            "prediction_steps_ahead": steps_ahead,
            "predictions": predictions,
            "predicted_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error predicting values for device {device_id}: {e}")
        return {"error": str(e)}
    finally:
        db.close()
