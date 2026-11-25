"""SQLite-backed fixed-window rate limits shared by Flask workers."""
import hashlib
import hmac
import sqlite3
import time
from pathlib import Path


class SQLiteRateLimiter:
    def __init__(self, database_path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                'CREATE TABLE IF NOT EXISTS rate_limit_buckets ('
                'bucket TEXT PRIMARY KEY, window_start INTEGER NOT NULL, hits INTEGER NOT NULL)'
            )

    def _connect(self):
        db = sqlite3.connect(self.database_path, timeout=10, isolation_level=None)
        db.execute('PRAGMA journal_mode=WAL')
        return db

    def hit(self, bucket, limit, window_seconds, now=None):
        now = int(time.time() if now is None else now)
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute(
                'SELECT window_start, hits FROM rate_limit_buckets WHERE bucket = ?', (bucket,)
            ).fetchone()
            if row is None or now - row[0] >= window_seconds:
                db.execute(
                    'INSERT INTO rate_limit_buckets (bucket, window_start, hits) VALUES (?, ?, 1) '
                    'ON CONFLICT(bucket) DO UPDATE SET window_start=excluded.window_start, hits=1',
                    (bucket, now),
                )
                allowed, retry_after = True, 0
            elif row[1] >= limit:
                allowed, retry_after = False, max(1, window_seconds - (now - row[0]))
            else:
                db.execute('UPDATE rate_limit_buckets SET hits = hits + 1 WHERE bucket = ?', (bucket,))
                allowed, retry_after = True, 0
            db.execute('DELETE FROM rate_limit_buckets WHERE window_start < ?', (now - window_seconds,))
            db.commit()
        return allowed, retry_after


def request_bucket(secret, address, route):
    raw = f'{route}:{address or "unknown"}'.encode()
    return hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
