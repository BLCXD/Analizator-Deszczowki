"""Private Compose service for starting development-only Raspberry agents."""
import hashlib
import hmac
import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


ROOT = '/opt/ad'
TOKEN = os.environ.get('MOCK_RUNNER_TOKEN', '')
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://backend:8000')
DB_DIR = os.environ.get('DB_DIR', '/data')
INTERVAL = max(5, int(os.environ.get('MOCK_INTERVAL_SECONDS', '30')))
if len(TOKEN) < 32:
    raise RuntimeError('MOCK_RUNNER_TOKEN must contain at least 32 characters')

agents = {}
agents_lock = threading.Lock()


class Agent:
    def __init__(self, device_id, secret):
        self.device_id = device_id
        self.secret = secret
        self.stop_event = threading.Event()
        self.thread = None
        self.process = None
        self.start()

    def start(self):
        if self.thread and self.thread.is_alive():
            return False
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.run, name=f'mock-{self.device_id}', daemon=True)
        self.thread.start()
        return True

    def run(self):
        env = {
            'PATH': os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin'),
            'BACKEND_URL': BACKEND_URL,
            'DEVICE_ID': self.device_id,
            'DEVICE_SECRET': self.secret,
            'USE_MOCK_SENSOR': 'true',
            'DB_PATH': os.path.join(DB_DIR, hashlib.sha256(self.device_id.encode()).hexdigest() + '.sqlite'),
            'SYNC_INTERVAL': str(INTERVAL),
            'HEARTBEAT_INTERVAL': str(INTERVAL),
        }
        command = ['/usr/local/bin/python', '-m', 'raspberry.ad_agent.main', '--once']
        while not self.stop_event.is_set():
            try:
                process = subprocess.Popen(command, cwd=ROOT, env=env,
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.process = process
                while process.poll() is None and not self.stop_event.wait(0.2):
                    pass
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                self.process = None
                if process.returncode != 0 and not self.stop_event.is_set():
                    print(f'Mock agent for {self.device_id} could not sync; queued data will retry.', flush=True)
            except OSError:
                print(f'Mock agent for {self.device_id} could not start; the next cycle will retry.', flush=True)
            self.stop_event.wait(INTERVAL)

    def stop(self):
        self.stop_event.set()
        if self.process and self.process.poll() is None:
            self.process.terminate()
        if self.thread:
            self.thread.join(timeout=5)


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self):
        return hmac.compare_digest(self.headers.get('Authorization', ''), f'Bearer {TOKEN}')

    def do_GET(self):
        if self.path == '/health':
            return self._reply(200, {'status': 'ok'})
        if not self._authorized():
            return self._reply(401, {'error': 'unauthorized'})
        parsed = urlparse(self.path)
        if parsed.path == '/api/agents':
            with agents_lock:
                return self._reply(200, {'agents': {device_id: agent.thread.is_alive() for device_id, agent in agents.items()}})
        return self._reply(404, {'error': 'not found'})

    def do_POST(self):
        if not self._authorized():
            return self._reply(401, {'error': 'unauthorized'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size < 0 or size > 4096:
                return self._reply(413, {'error': 'request too large'})
            payload = json.loads(self.rfile.read(size))
        except (ValueError, json.JSONDecodeError):
            return self._reply(400, {'error': 'invalid request'})

        raw_device_id = payload.get('device_id', '')
        if not isinstance(raw_device_id, str):
            return self._reply(422, {'error': 'invalid device credentials'})
        device_id = raw_device_id.strip()
        path = urlparse(self.path).path
        if path == '/api/agents/start':
            secret = payload.get('device_secret', '')
            if len(device_id) < 3 or len(device_id) > 100 or any(ord(char) < 32 for char in device_id):
                return self._reply(422, {'error': 'invalid device credentials'})
            with agents_lock:
                if device_id in agents:
                    agents[device_id].start()
                    return self._reply(202, {'status': 'started'})
                if not isinstance(secret, str) or len(secret) < 32 or len(secret) > 256:
                    return self._reply(422, {'error': 'private key is required for first start'})
                agents[device_id] = Agent(device_id, secret)
            return self._reply(202, {'status': 'started'})

        if path == '/api/agents/stop':
            with agents_lock:
                agent = agents.get(device_id)
            if agent:
                agent.stop()
            return self._reply(200, {'status': 'stopped'})

        if path == '/api/agents/delete':
            with agents_lock:
                agent = agents.pop(device_id, None)
            if agent:
                agent.stop()
                agent.secret = ''
            return self._reply(200, {'status': 'deleted'})
        return self._reply(404, {'error': 'not found'})

    def log_message(self, _format, *_args):
        return


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', 8090), Handler).serve_forever()
