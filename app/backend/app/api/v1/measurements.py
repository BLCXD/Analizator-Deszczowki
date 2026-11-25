from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, BackgroundTasks, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Union
from datetime import datetime, timedelta, timezone
import time
import json
import asyncio
import httpx
from app.db.session import get_db
from app.db.session import SessionLocal
from app.api.v1.auth import get_current_user
from app.core.security import verify_token
from app.services.measurement import (
    create_measurement,
    get_measurement,
    get_measurements_by_device,
    get_latest_measurement_by_device,
    get_measurements_since_timestamp
)
from app.services.device import can_access_device, get_device_by_id
from app.schemas.measurement import MeasurementCreate, Measurement
from app.models.user import User
from app.models.device import Device
from app.models.measurement import Measurement as SQLMeasurement
from app.analysis.service import analysis_service
from app.services.ai_analysis import analyze_measurements_with_nvidia, AIAnalysisError

router = APIRouter()


@router.post("/{device_id}/analysis/ai")
def get_ai_measurement_analysis(
    device_id: str,
    hours: int = Query(168, ge=1, le=720),
    city: Optional[str] = Query(None, min_length=1, max_length=120),
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user),
):
                                                                                    
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    if isinstance(current_user, dict) or device.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this device")

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = (
        db.query(SQLMeasurement)
        .filter(SQLMeasurement.device_id == device.id, SQLMeasurement.measurement_time >= since)
        .order_by(SQLMeasurement.measurement_time.desc())
        .limit(120)
        .all()
    )
    measurements = [
        {
            "time": row.measurement_time.isoformat() if row.measurement_time else None,
            "ph": row.water_quality_ph,
            "turbidity_ntu": row.water_quality_turbidity,
            "conductivity_us_cm": row.ec,
            "temperature_c": row.temperature,
            "rainfall_mm": row.rainfall_mm,
            "rainfall_1h_mm": row.rainfall_1h_mm,
        }
        for row in reversed(rows)
    ]
    if not measurements:
        return {
            "analysis": "Brak pomiarów w wybranym okresie. Zbierz kilka odczytów, aby zobaczyć podsumowanie zmian.",
            "measurement_count": 0,
            "period_hours": hours,
            "disclaimer": "Analiza AI jest informacyjna i nie potwierdza bezpieczeństwa wody ani dokładności czujników.",
        }
    try:
        weather = None
        weather_location_error = None
        if city:
            try:
                location_response = httpx.get(
                    "https://geocoding-api.open-meteo.com/v1/search",
                    params={"name": city, "count": 1, "language": "pl", "format": "json"},
                    timeout=httpx.Timeout(8.0, connect=3.0),
                )
                location_response.raise_for_status()
                results = location_response.json().get("results", [])
                if results:
                    latitude, longitude = results[0]["latitude"], results[0]["longitude"]
                else:
                    weather_location_error = "Nie znaleziono miasta. Sprawdź nazwę albo wybierz lokalizację przeglądarki."
            except (httpx.HTTPError, ValueError, TypeError, KeyError, IndexError):
                latitude = longitude = None
                weather_location_error = "Nie udało się znaleźć miasta. Spróbuj ponownie albo wybierz lokalizację przeglądarki."
        if latitude is not None and longitude is not None:
            try:
                weather_response = httpx.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "hourly": "temperature_2m,precipitation",
                        "past_days": min(5, (hours + 23) // 24),
                        "forecast_days": 1,
                        "timezone": "UTC",
                    },
                    timeout=httpx.Timeout(8.0, connect=3.0),
                )
                weather_response.raise_for_status()
                hourly = weather_response.json().get("hourly", {})
                weather = {"time": hourly.get("time", [])[-hours:],
                           "temperature_c": hourly.get("temperature_2m", [])[-hours:],
                           "precipitation_mm": hourly.get("precipitation", [])[-hours:]}
            except (httpx.HTTPError, ValueError, TypeError):
                weather = None
        analysis = analyze_measurements_with_nvidia(measurements, hours, weather)
    except AIAnalysisError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.public_message) from exc
    return {
        "analysis": analysis,
        "measurement_count": len(measurements),
        "period_hours": hours,
        "weather_error": weather_location_error,
        "disclaimer": "Analiza AI jest informacyjna i nie potwierdza bezpieczeństwa wody ani dokładności czujników.",
    }



class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, device_id: str):
        await websocket.accept(subprotocol="ad-stream")
        if device_id not in self.active_connections:
            self.active_connections[device_id] = []
        self.active_connections[device_id].append(websocket)

    def disconnect(self, websocket: WebSocket, device_id: str):
        if device_id in self.active_connections:
            if websocket in self.active_connections[device_id]:
                self.active_connections[device_id].remove(websocket)
            if not self.active_connections[device_id]:
                del self.active_connections[device_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_device(self, message: str, device_id: str):
        if device_id in self.active_connections:
            for connection in list(self.active_connections[device_id]):
                try:
                    await connection.send_text(message)
                except (WebSocketDisconnect, RuntimeError):
                    self.disconnect(connection, device_id)


manager = ConnectionManager()


@router.post("/", response_model=Measurement, status_code=status.HTTP_201_CREATED)
def create_measurement_endpoint(
    measurement_in: MeasurementCreate,
    background_tasks: BackgroundTasks,
    response: Response,
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user)
):
\
\
\
       
    device = get_device_by_id(db, measurement_in.device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    if not can_access_device(device, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add measurements to this device"
        )

    measurement_data = measurement_in.model_dump(exclude={'device_id'})
    measurement_id = measurement_data.get('measurement_id')

    if measurement_id:
        existing_measurement = get_measurement(db, measurement_id)
        if existing_measurement:
            if existing_measurement.device_id != device.id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Measurement ID already used")
            response.status_code = status.HTTP_200_OK
            return existing_measurement

    try:
        measurement = create_measurement(db=db, measurement_in=measurement_in)
    except IntegrityError:
        db.rollback()
        existing_measurement = get_measurement(db, measurement_id) if measurement_id else None
        if existing_measurement and existing_measurement.device_id == device.id:
            response.status_code = status.HTTP_200_OK
            return existing_measurement
        if existing_measurement:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Measurement ID already used")
        raise

    measurement_dict = {
        "type": "measurement",
        "device_id": measurement_in.device_id,
        "timestamp": measurement.measurement_time.isoformat(),
        "data": {
            "ph": measurement.water_quality_ph,
            "ec": measurement.ec,
            "turbidity": measurement.water_quality_turbidity,
            "temperature": measurement.temperature
        }
    }
    background_tasks.add_task(manager.broadcast_to_device,
        json.dumps(measurement_dict),
        measurement_in.device_id
    )

    return measurement


@router.get("/", response_model=List[Measurement])
def get_measurements(
    device_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user)
):
\
\
       
    query = db.query(SQLMeasurement)

    if isinstance(current_user, dict):
        authorized_device_id = current_user.get("device_id")
        if not authorized_device_id or device_id != authorized_device_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Device access denied")
        query = query.filter(SQLMeasurement.device_id == current_user["id"])

    if device_id:
        device = get_device_by_id(db, device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )

        if not can_access_device(device, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this device"
            )

        query = query.filter(SQLMeasurement.device_id == device.id)

    if start_time:
        query = query.filter(SQLMeasurement.measurement_time >= start_time)
    if end_time:
        query = query.filter(SQLMeasurement.measurement_time <= end_time)
    if start_time and end_time and start_time > end_time:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="start_time must be before end_time")
    if not isinstance(current_user, dict) and not device_id:
        query = query.filter(SQLMeasurement.device_id.in_(
            db.query(Device.id).filter(Device.user_id == current_user.id)
        ))

    measurements = query.order_by(SQLMeasurement.measurement_time.desc()).offset(skip).limit(limit).all()
    return measurements


@router.get("/{device_id}/latest", response_model=Measurement)
def get_latest_measurement(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user)
):
\
\
       
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if not can_access_device(device, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this device"
        )

    measurement = get_latest_measurement_by_device(db, device.id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No measurements found for this device"
        )
    return measurement


@router.get("/{device_id}", response_model=List[Measurement])
def get_measurements_by_device_endpoint(
    device_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user)
):
\
\
       
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if not can_access_device(device, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this device"
        )

    measurements = get_measurements_by_device(
        db, device.id, skip=skip, limit=limit, start_time=start_time, end_time=end_time
    )
    return measurements


@router.get("/{device_id}/analysis/trends")
def get_measurement_trends(
    device_id: str,
    hours: int = Query(24, ge=1, le=8760),
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user)
):
\
\
       
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if not can_access_device(device, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this device"
        )

    measurements = get_measurements_since_timestamp(
        db, device.id, datetime.now(timezone.utc) - timedelta(hours=hours)
    )

    measurement_dicts = []
    for m in measurements:
        measurement_dicts.append({
            "measurement_time": m.measurement_time.isoformat() if m.measurement_time else None,
            "device_id": m.device_id,
            "rainfall_mm": m.rainfall_mm,
            "rainfall_1h_mm": m.rainfall_1h_mm,
            "water_quality_ph": m.water_quality_ph,
            "water_quality_turbidity": m.water_quality_turbidity,
            "ec": m.ec,
            "temperature": m.temperature,
            "humidity": m.humidity
        })

    trends = analysis_service.analyze_trends(measurement_dicts)
    return {
        "device_id": device_id,
        "time_period_hours": hours,
        "measurement_count": len(measurements),
        "trends": trends
    }


@router.get("/{device_id}/analysis/anomalies")
def get_measurement_anomalies(
    device_id: str,
    hours: int = Query(24, ge=1, le=8760),
    db: Session = Depends(get_db),
    current_user: Union[User, dict] = Depends(get_current_user)
):
\
\
       
    device = get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if not can_access_device(device, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this device"
        )

    measurements = get_measurements_since_timestamp(
        db, device.id, datetime.now(timezone.utc) - timedelta(hours=hours)
    )

    measurement_dicts = []
    for m in measurements:
        measurement_dicts.append({
            "measurement_time": m.measurement_time.isoformat() if m.measurement_time else None,
            "device_id": m.device_id,
            "rainfall_mm": m.rainfall_mm,
            "rainfall_1h_mm": m.rainfall_1h_mm,
            "water_quality_ph": m.water_quality_ph,
            "water_quality_turbidity": m.water_quality_turbidity,
            "ec": m.ec,
            "temperature": m.temperature,
            "humidity": m.humidity
        })

    anomalies = analysis_service.detect_anomalies(measurement_dicts)
    return {
        "device_id": device_id,
        "time_period_hours": hours,
        "measurement_count": len(measurements),
        "anomalies": anomalies
    }


@router.websocket("/ws/{device_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    device_id: str,
):
                                                                                  
    offered_protocols = [part.strip() for part in websocket.headers.get("sec-websocket-protocol", "").split(",")]
    ticket = next((part.removeprefix("ticket.") for part in offered_protocols if part.startswith("ticket.")), None)
    payload = verify_token(ticket) if ticket else None
    if not payload or payload.get("type") != "stream" or payload.get("sub") != device_id:
        await websocket.close(code=4401)
        return

    db = SessionLocal()
    try:
        device = get_device_by_id(db, device_id)
        if not device or not device.is_active or not device.user_id:
            await websocket.close(code=4403)
            return
    finally:
        db.close()

    await manager.connect(websocket, device_id)
    try:
        while True:
            if time.time() >= payload.get("exp", 0):
                await websocket.close(code=4401)
                break
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=10)
            except asyncio.TimeoutError:
                continue
    except WebSocketDisconnect:
        return
    finally:
        manager.disconnect(websocket, device_id)
