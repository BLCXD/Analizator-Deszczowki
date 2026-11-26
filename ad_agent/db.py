"""
Database handler for Raspberry Pi Agent using SQLite
"""

import sqlite3
import threading
import os
from datetime import datetime
from typing import List, Dict, Any
from contextlib import contextmanager


class MeasurementQueueDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_db()

    def init_db(self):
                                                          
        parent = os.path.dirname(os.path.abspath(self.db_path))
        os.makedirs(parent, exist_ok=True)
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    measurement_id TEXT UNIQUE NOT NULL,
                    device_id TEXT NOT NULL,
                    water_quality_turbidity REAL,
                    ec REAL,
                    water_quality_ph REAL,
                    temperature REAL,
                    humidity REAL,
                    rainfall_mm REAL,
                    rainfall_1h_mm REAL,
                    raw_data TEXT,
                    timestamp TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    sent INTEGER DEFAULT 0,
                    retry_count INTEGER DEFAULT 0,
                    next_attempt_at TEXT
                )
            ''')

            columns = {row[1] for row in conn.execute("PRAGMA table_info(measurements)")}
            if "next_attempt_at" not in columns:
                conn.execute("ALTER TABLE measurements ADD COLUMN next_attempt_at TEXT")
            for column in ("ec", "rainfall_mm", "rainfall_1h_mm"):
                if column not in columns:
                    conn.execute(f"ALTER TABLE measurements ADD COLUMN {column} REAL")

            if "water_level" in columns:
                conn.execute('''
                    CREATE TABLE measurements_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        measurement_id TEXT UNIQUE NOT NULL,
                        device_id TEXT NOT NULL,
                        water_quality_turbidity REAL,
                        ec REAL,
                        water_quality_ph REAL,
                        temperature REAL,
                        humidity REAL,
                        rainfall_mm REAL,
                        rainfall_1h_mm REAL,
                        raw_data TEXT,
                        timestamp TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        sent INTEGER DEFAULT 0,
                        retry_count INTEGER DEFAULT 0,
                        next_attempt_at TEXT
                    )
                ''')
                conn.execute('''
                    INSERT INTO measurements_new
                    (id, measurement_id, device_id, water_quality_turbidity, ec,
                     water_quality_ph, temperature, humidity, rainfall_mm,
                     rainfall_1h_mm, raw_data, timestamp, created_at, sent, retry_count, next_attempt_at)
                    SELECT id, measurement_id, device_id, water_quality_turbidity, ec,
                           water_quality_ph, temperature, humidity, rainfall_mm,
                           rainfall_1h_mm, raw_data, timestamp, created_at, sent, retry_count, next_attempt_at
                    FROM measurements
                ''')
                conn.execute("DROP TABLE measurements")
                conn.execute("ALTER TABLE measurements_new RENAME TO measurements")

            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_measurements_sent
                ON measurements(sent)
            ''')

            conn.commit()

    @contextmanager
    def get_connection(self):
                                                               
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def add_measurement(self, measurement: Dict[str, Any]) -> bool:
                                            
        with self.lock:
            try:
                with self.get_connection() as conn:
                    conn.execute('''
                        INSERT OR IGNORE INTO measurements
                        (measurement_id, device_id, water_quality_turbidity, ec,
                         water_quality_ph, temperature, humidity, rainfall_mm,
                         rainfall_1h_mm, raw_data, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        measurement.get('measurement_id'),
                        measurement.get('device_id'),
                        measurement.get('water_quality_turbidity'),
                        measurement.get('ec'),
                        measurement.get('water_quality_ph'),
                        measurement.get('temperature'),
                        measurement.get('humidity'),
                        measurement.get('rainfall_mm'),
                        measurement.get('rainfall_1h_mm'),
                        measurement.get('raw_data'),
                        measurement.get('timestamp')
                    ))
                    conn.commit()
                    return conn.total_changes > 0
            except Exception as e:
                print(f"Error adding measurement to queue: {e}")
                return False

    def contains_measurement(self, measurement_id: str) -> bool:
                                                                                  
        with self.lock:
            try:
                with self.get_connection() as conn:
                    return conn.execute(
                        "SELECT 1 FROM measurements WHERE measurement_id = ? LIMIT 1",
                        (measurement_id,),
                    ).fetchone() is not None
            except Exception as e:
                print(f"Error checking measurement queue: {e}")
                return False

    def get_unsent_measurements(self, limit: int = 100) -> List[Dict[str, Any]]:
                                                         
        with self.lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.execute('''
                        SELECT * FROM measurements
                        WHERE sent = 0
                          AND (next_attempt_at IS NULL OR next_attempt_at <= ?)
                        ORDER BY created_at ASC
                        LIMIT ?
                    ''', (datetime.utcnow().isoformat(), limit))

                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
            except Exception as e:
                print(f"Error getting unsent measurements: {e}")
                return []

    def get_unsent_count(self) -> int:
                                                  
        with self.lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.execute('''
                        SELECT COUNT(*) FROM measurements
                        WHERE sent = 0
                    ''')
                    result = cursor.fetchone()
                    return result[0] if result else 0
            except Exception as e:
                print(f"Error getting unsent count: {e}")
                return 0

    def mark_as_sent(self, measurement_ids: List[int]) -> int:
                                       
        with self.lock:
            if not measurement_ids:
                return 0

            try:
                with self.get_connection() as conn:
                    placeholders = ','.join(['?'] * len(measurement_ids))
                    cursor = conn.execute(f'''
                        UPDATE measurements
                        SET sent = 1
                        WHERE id IN ({placeholders})
                    ''', measurement_ids)
                    conn.commit()
                    return cursor.rowcount
            except Exception as e:
                print(f"Error marking measurements as sent: {e}")
                return 0

    def increment_retry_count(self, measurement_ids: List[int]) -> int:
                                                    
        with self.lock:
            if not measurement_ids:
                return 0

            try:
                with self.get_connection() as conn:
                    placeholders = ','.join(['?'] * len(measurement_ids))
                    cursor = conn.execute(f'''
                        UPDATE measurements
                        SET retry_count = retry_count + 1,
                            next_attempt_at = strftime('%Y-%m-%dT%H:%M:%f', 'now', '+' ||
                                min(60, (1 << min(retry_count, 6))) || ' seconds')
                        WHERE id IN ({placeholders})
                    ''', measurement_ids)
                    conn.commit()
                    return cursor.rowcount
            except Exception as e:
                print(f"Error incrementing retry count: {e}")
                return 0

    def get_stats(self) -> Dict[str, int]:
                                  
        with self.lock:
            try:
                with self.get_connection() as conn:
                    cursor = conn.execute('''
                        SELECT
                            COUNT(*) as total,
                            SUM(CASE WHEN sent = 0 THEN 1 ELSE 0 END) as unsent,
                            SUM(CASE WHEN sent = 1 THEN 1 ELSE 0 END) as sent,
                            MAX(retry_count) as max_retries
                        FROM measurements
                    ''')
                    row = cursor.fetchone()
                    return dict(row) if row else {}
            except Exception as e:
                print(f"Error getting stats: {e}")
                return {}
