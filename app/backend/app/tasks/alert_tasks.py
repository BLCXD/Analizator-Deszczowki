import json
import logging
import smtplib
from datetime import datetime, timedelta
from typing import Any, Dict

from backend.app.tasks.celery_config import celery_app
from backend.app.db.session import SessionLocal
from backend.app.services.measurement import get_latest_measurement_by_device, get_measurements_since_timestamp
from backend.app.services.device import get_device_by_id, get_devices_by_user
from backend.app.services.push import send_to_user
from backend.app.services.email import send_email
from backend.app.analysis.service import analysis_service

logger = logging.getLogger(__name__)

def send_alert_email(to_email: str, subject: str, body: str):
                                                            
    try:
        return send_email(to_email, subject, body)
    except (OSError, smtplib.SMTPException, ValueError):
        logger.error("Alert email delivery failed")
        return False

@celery_app.task
def check_device_alerts(device_id: str, user_id: int, thresholds: Dict[str, Any]):
\
\
\
       
    db = SessionLocal()
    try:
        device = get_device_by_id(db, device_id)
        if not device:
            logger.warning(f"Device {device_id} not found")
            return {"error": "Device not found"}

        if device.user_id != user_id:
            logger.warning(f"User {user_id} not authorized for device {device_id}")
            return {"error": "Not authorized"}

        measurement = get_latest_measurement_by_device(db, device.id)
        if not measurement:
            logger.info(f"No measurements found for device {device_id}")
            return {"info": "No measurements found"}

        measurement_dict = {
            "measurement_time": measurement.measurement_time.isoformat() if measurement.measurement_time else None,
            "device_id": measurement.device_id,
            "water_quality_ph": measurement.water_quality_ph,
            "water_quality_turbidity": measurement.water_quality_turbidity,
            "temperature": measurement.temperature,
            "humidity": measurement.humidity
        }

        alerts = analysis_service.check_alert_thresholds(measurement_dict, thresholds)

        if not alerts:
            logger.debug(f"No alerts for device {device_id}")
            return {
                "device_id": device_id,
                "alert_count": 0,
                "checked_at": datetime.utcnow().isoformat()
            }

        logger.info(f"Found {len(alerts)} alerts for device {device_id}")
        alert_messages = [alert["message"] for alert in alerts]
        logger.warning(f"ALERTS for device {device_id}: {'; '.join(alert_messages)}")

        payload = json.dumps(
            {
                "title": "Analizator Deszczówki — alert",
                "body": "; ".join(alert_messages),
                "device_id": device_id,
            }
        )
        try:
            result = send_to_user(db, device.user_id, payload)
            logger.info(f"Push delivery for device {device_id}: {result}")
        except Exception as exc:
            logger.error(f"Push delivery failed for device {device_id}: {exc}")

        return {
            "device_id": device_id,
            "alert_count": len(alerts),
            "alerts": alerts,
            "checked_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error checking alerts for device {device_id}: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task
def check_all_user_device_alerts(user_id: int):
\
\
\
       
    db = SessionLocal()
    try:
        devices = get_devices_by_user(db, user_id)
        if not devices:
            logger.info(f"No devices found for user {user_id}")
            return {"info": "No devices found"}

        results = []
        for device in devices:
            thresholds = {
                "ph": {"min": 5.0, "max": 9.0},
                "temperature": {"min": 0, "max": 40},
                "turbidity": {"max": 10.0}
            }

            result = check_device_alerts(str(device.device_id), user_id, thresholds)
            results.append({
                "device_id": str(device.device_id),
                "device_name": device.name,
                "result": result
            })

        return {
            "user_id": user_id,
            "device_count": len(devices),
            "results": results,
            "checked_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error checking alerts for user {user_id}: {e}")
        return {"error": str(e)}
    finally:
        db.close()

@celery_app.task
def generate_periodic_analysis_report(user_id: int, hours: int = 24):
\
\
\
       
    db = SessionLocal()
    try:
        devices = get_devices_by_user(db, user_id)
        if not devices:
            logger.info(f"No devices found for user {user_id}")
            return {"info": "No devices found"}

        report = {
            "user_id": user_id,
            "report_period_hours": hours,
            "generated_at": datetime.utcnow().isoformat(),
            "devices": []
        }

        since_time = datetime.utcnow() - timedelta(hours=hours)

        for device in devices:
            measurements = get_measurements_since_timestamp(
                db=db,
                device_id=str(device.device_id),
                since=since_time
            )

            measurement_dicts = []
            for m in measurements:
                measurement_dicts.append({
                    "measurement_time": m.measurement_time.isoformat() if m.measurement_time else None,
                    "device_id": m.device_id,
                    "water_quality_ph": m.water_quality_ph,
                    "water_quality_turbidity": m.water_quality_turbidity,
                    "temperature": m.temperature,
                    "humidity": m.humidity
                })

            if measurement_dicts:
                trends = analysis_service.analyze_trends(measurement_dicts)
                anomalies = analysis_service.detect_anomalies(measurement_dicts)
                predictions = analysis_service.predict_next_values(measurement_dicts, steps_ahead=3)

                device_report = {
                    "device_id": str(device.device_id),
                    "device_name": device.name,
                    "measurement_count": len(measurements),
                    "trends": trends,
                    "anomaly_count": len(anomalies),
                    "recent_anomalies": anomalies[:5] if anomalies else [],
                    "predictions": predictions
                }
                report["devices"].append(device_report)
            else:
                report["devices"].append({
                    "device_id": str(device.device_id),
                    "device_name": device.name,
                    "measurement_count": 0,
                    "info": "No measurements in period"
                })

        logger.info(f"Generated analysis report for user {user_id} with {len(devices)} devices")
        return report

    except Exception as e:
        logger.error(f"Error generating analysis report for user {user_id}: {e}")
        return {"error": str(e)}
    finally:
        db.close()
