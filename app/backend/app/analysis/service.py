import base64
import io
import json
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt


class AnalysisService:
    def __init__(self):
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.trend_model = LinearRegression()

    def analyze_trends(self, measurements: List[Dict]) -> Dict[str, Any]:
        if not measurements or len(measurements) < 2:
            return {"error": "Insufficient data for trend analysis"}

        df = pd.DataFrame(measurements)
        df['timestamp'] = pd.to_datetime(df['measurement_time'])
        df = df.sort_values('timestamp')

        df['seconds'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()

        trends = {}
        for column in ['water_quality_ph', 'temperature']:
            if column in df.columns and df[column].notna().any():
                X = df[['seconds']]
                y = df[column].dropna()
                if len(y) > 1:
                    self.trend_model.fit(X[:len(y)], y)
                    slope = self.trend_model.coef_[0]
                    if slope > 0.01:
                        direction = "increasing"
                    elif slope < -0.01:
                        direction = "decreasing"
                    else:
                        direction = "stable"
                    strength = min(abs(slope) * 1000, 10)
                    trends[column] = {
                        "direction": direction,
                        "slope": float(slope),
                        "strength": float(strength),
                        "latest": float(y.iloc[-1]) if len(y) > 0 else None
                    }
                else:
                    trends[column] = {"error": "Insufficient data points"}
            else:
                trends[column] = {"error": "Column not found or all NaN"}

        return trends

    def detect_anomalies(self, measurements: List[Dict]) -> List[Dict]:
        if not measurements or len(measurements) < 10:
            return []

        df = pd.DataFrame(measurements)
        numeric_cols = ['water_quality_ph', 'temperature', 'water_quality_turbidity']
        available_cols = [col for col in numeric_cols if col in df.columns]

        if not available_cols:
            return []

        data = df[available_cols].fillna(method='ffill').fillna(method='bfill')
        if data.isnull().any().any():
            data = data.dropna()

        if len(data) < 10:
            return []

        self.anomaly_detector.fit(data)
        predictions = self.anomaly_detector.predict(data)

        anomalies = df.iloc[predictions == -1]
        return anomalies.to_dict('records')

    def predict_next_values(self, measurements: List[Dict], steps_ahead: int = 5) -> Dict[str, Any]:
        if not measurements or len(measurements) < 5:
            return {"error": "Insufficient data for prediction"}

        df = pd.DataFrame(measurements)
        df['timestamp'] = pd.to_datetime(df['measurement_time'])
        df = df.sort_values('timestamp')
        df['seconds'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()

        predictions = {}
        for column in ['water_quality_ph', 'temperature']:
            if column in df.columns and df[column].notna().any():
                X = df[['seconds']]
                y = df[column].dropna()
                if len(y) > 1:
                    self.trend_model.fit(X[:len(y)], y)
                    last_second = df['seconds'].iloc[-1]
                    future_seconds = np.array([last_second + i * 300 for i in range(1, steps_ahead+1)]).reshape(-1, 1)
                    future_preds = self.trend_model.predict(future_seconds)
                    predictions[column] = {
                        "predictions": [float(pred) for pred in future_preds],
                        "timesteps_ahead": list(range(1, steps_ahead+1))
                    }
                else:
                    predictions[column] = {"error": "Insufficient data points"}
            else:
                predictions[column] = {"error": "Column not found or all NaN"}

        return predictions

    def export_to_csv(self, measurements: List[Dict]) -> str:
        if not measurements:
            return ""

        df = pd.DataFrame(measurements)
        preferred_order = ['measurement_time', 'device_id', 'water_quality_ph',
                          'water_quality_turbidity', 'ec', 'temperature', 'humidity']
        existing_cols = [col for col in preferred_order if col in df.columns]
        other_cols = [col for col in df.columns if col not in preferred_order]
        df = df[existing_cols + other_cols]

        return df.to_csv(index=False)

    def export_to_json(self, measurements: List[Dict]) -> str:
        return json.dumps(measurements, indent=2, default=str)

    def generate_trend_plot(self, measurements: List[Dict], metric: str = 'water_quality_ph') -> str:
        if not measurements or len(measurements) < 2:
            return ""

        df = pd.DataFrame(measurements)
        df['timestamp'] = pd.to_datetime(df['measurement_time'])
        df = df.sort_values('timestamp')

        if metric not in df.columns:
            return ""

        plt.figure(figsize=(10, 6))
        plt.plot(df['timestamp'], df[metric], 'b-o', linewidth=2, markersize=4)
        plt.title(f'{metric.replace("_", " ").title()} Trend')
        plt.xlabel('Time')
        plt.ylabel(metric.replace("_", " ").title())
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(True, alpha=0.3)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{image_base64}"

    def check_alert_thresholds(self, measurement: Dict, thresholds: Dict) -> List[Dict]:
        alerts = []
        if not thresholds:
            return alerts

        metric_map = {
            'ph': ('water_quality_ph', 'pH units'),
            'temperature': ('temperature', '°C'),
            'turbidity': ('water_quality_turbidity', 'NTU')
        }

        for alert_key, (db_key, unit) in metric_map.items():
            if alert_key in thresholds and db_key in measurement:
                value = measurement[db_key]
                if value is None:
                    continue

                threshold = thresholds[alert_key]
                if isinstance(threshold, dict):
                    if 'min' in threshold and value < threshold['min']:
                        alerts.append({
                            "metric": alert_key,
                            "value": value,
                            "unit": unit,
                            "type": "below_min",
                            "threshold": threshold['min'],
                            "message": f"{alert_key} ({value} {unit}) is below minimum threshold ({threshold['min']} {unit})"
                        })
                    if 'max' in threshold and value > threshold['max']:
                        alerts.append({
                            "metric": alert_key,
                            "value": value,
                            "unit": unit,
                            "type": "above_max",
                            "threshold": threshold['max'],
                            "message": f"{alert_key} ({value} {unit}) exceeds maximum threshold ({threshold['max']} {unit})"
                        })
                else:
                    if value > threshold:
                        alerts.append({
                            "metric": alert_key,
                            "value": value,
                            "unit": unit,
                            "type": "above_threshold",
                            "threshold": threshold,
                            "message": f"{alert_key} ({value} {unit}) exceeds threshold ({threshold} {unit})"
                        })

        return alerts

analysis_service = AnalysisService()
