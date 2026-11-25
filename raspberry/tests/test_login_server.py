import json
import threading
import time
import unittest
import urllib.request
import urllib.error
import tempfile
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ad_agent.login_server import LoginServer


class FakeBackend(ThreadingHTTPServer):
    def __init__(self):
        super().__init__(("127.0.0.1", 0), FakeHandler)
        self.port = self.server_address[1]


class FakeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode()
        import urllib.parse as up
        params = up.parse_qs(body)
        email = params.get("username", [""])[0]
        pw = params.get("password", [""])[0]
        if email == "user@example.com" and pw == "secret":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"access_token": "fake-jwt-token", "token_type": "bearer"}).encode())
        else:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"detail": "bad credentials"}).encode())

    def log_message(self, *args):
        pass


class LoginServerTests(unittest.TestCase):
    def setUp(self):
        self.backend = FakeBackend()
        self.t = threading.Thread(target=self.backend.serve_forever, daemon=True)
        self.t.start()
        time.sleep(0.2)

        self.login = LoginServer(backend_url=f"http://127.0.0.1:{self.backend.port}", host="127.0.0.1", port=0, session_secret="test-session-secret-that-is-long-enough")
        self.login.port = self.login.server.server_address[1]
        self.login_thread = threading.Thread(target=self.login.server.serve_forever, daemon=True)
        self.login_thread.start()
        time.sleep(0.2)

    def tearDown(self):
        self.login.close()
        self.backend.shutdown()

    def _post(self, email, password):
        data = json.dumps({"email": email, "password": password}).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.login.port}/api/login",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return urllib.request.urlopen(req)

    def test_login_page_served(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.login.port}/login") as resp:
            body = resp.read().decode()
        self.assertIn("Logowanie", body)

    def test_successful_login_sets_session_cookie(self):
        resp = self._post("user@example.com", "secret")
        self.assertEqual(resp.status, 200)
        cookies = resp.headers.get_all("Set-Cookie")
        self.assertTrue(any("ad_session=" in c and "HttpOnly" in c and "SameSite=Lax" in c for c in cookies))

    def test_bad_credentials_return_401(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._post("user@example.com", "wrong")
        self.assertEqual(ctx.exception.code, 401)

    def test_dashboard_and_status_require_valid_local_session(self):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.login.port}/api/status") as response:
            self.assertEqual(response.status, 200)
            self.assertNotIn(b"device_id", response.read())
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(f"http://127.0.0.1:{self.login.port}/api/local-status")
        self.assertEqual(ctx.exception.code, 401)
        login = self._post("user@example.com", "secret")
        cookie = login.headers.get("Set-Cookie")
        self.assertIn("HttpOnly", cookie)
        self.assertIn("Max-Age=1800", cookie)
        self.assertIn("Secure", cookie)
        opener = urllib.request.build_opener()
        request = urllib.request.Request(f"http://127.0.0.1:{self.login.port}/dashboard", headers={"Cookie": cookie.split(";", 1)[0]})
        with opener.open(request) as response:
            self.assertEqual(response.status, 200)

    def test_device_secret_is_written_private_and_session_is_validated(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            secret_path = os.path.join(temp_dir, "device-secret")
            self.login.device_secret_path = __import__("pathlib").Path(secret_path)
            self.login._save_device_secret("x" * 50)
            self.assertEqual(open(secret_path).read().strip(), "x" * 50)
            self.assertEqual(os.stat(secret_path).st_mode & 0o777, 0o600)
            cookie = self.login._sign_session("fake-token")
            self.assertEqual(self.login._read_session(f"ad_session={cookie}"), "fake-token")
            self.assertIsNone(self.login._read_session("ad_session=invalid"))


if __name__ == "__main__":
    import unittest
    unittest.main()
