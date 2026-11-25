"""Small SQLite-backed Flask session store for deployments with multiple workers."""
import json
import secrets
import sqlite3
import time
from pathlib import Path

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict


class ServerSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(_):
            self.modified = True

        super().__init__(initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class SQLiteSessionInterface(SessionInterface):
                                                                                           

    def __init__(self, database_path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS flask_sessions ("
                "sid TEXT PRIMARY KEY, data TEXT NOT NULL, expires_at INTEGER NOT NULL)"
            )

    def _connect(self):
        db = sqlite3.connect(self.database_path, timeout=10)
        db.execute('PRAGMA journal_mode=WAL')
        return db

    def regenerate(self, session):
                                                                                     
        if session.sid:
            with self._connect() as db:
                db.execute('DELETE FROM flask_sessions WHERE sid = ?', (session.sid,))
        session.sid = secrets.token_urlsafe(32)
        session.modified = True

    def open_session(self, app, request):
        sid = request.cookies.get(self.get_cookie_name(app))
        if sid and len(sid) == 43 and all(char.isalnum() or char in '-_' for char in sid):
            with self._connect() as db:
                row = db.execute(
                    'SELECT data, expires_at FROM flask_sessions WHERE sid = ?', (sid,)
                ).fetchone()
                if row and row[1] > int(time.time()):
                    try:
                        session = ServerSession(json.loads(row[0]), sid=sid)
                    except (TypeError, ValueError):
                        session = None
                    if session is not None:
                        return session
                db.execute('DELETE FROM flask_sessions WHERE sid = ?', (sid,))
        return ServerSession(sid=secrets.token_urlsafe(32), new=True)

    def save_session(self, app, session, response):
        name = self.get_cookie_name(app)
        if not session:
            if session.sid:
                with self._connect() as db:
                    db.execute('DELETE FROM flask_sessions WHERE sid = ?', (session.sid,))
            response.delete_cookie(
                name,
                domain=self.get_cookie_domain(app),
                path=self.get_cookie_path(app),
                secure=self.get_cookie_secure(app),
                httponly=self.get_cookie_httponly(app),
                samesite=self.get_cookie_samesite(app),
            )
            return

        expires_in = int(app.permanent_session_lifetime.total_seconds())
        expires_at = int(time.time()) + expires_in
        payload = json.dumps(dict(session), separators=(',', ':'), ensure_ascii=False)
        with self._connect() as db:
            db.execute(
                'INSERT INTO flask_sessions (sid, data, expires_at) VALUES (?, ?, ?) '
                'ON CONFLICT(sid) DO UPDATE SET data = excluded.data, expires_at = excluded.expires_at',
                (session.sid, payload, expires_at),
            )
            db.execute('DELETE FROM flask_sessions WHERE expires_at <= ?', (int(time.time()),))

        response.set_cookie(
            name,
            session.sid,
            expires=self.get_expiration_time(app, session),
            httponly=self.get_cookie_httponly(app),
            secure=self.get_cookie_secure(app),
            samesite=self.get_cookie_samesite(app),
            domain=self.get_cookie_domain(app),
            path=self.get_cookie_path(app),
        )
