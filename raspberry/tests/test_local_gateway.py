import json
import tempfile
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from ad_agent.local_gateway import LocalGatewayServer
from ad_agent.db import MeasurementQueueDB


class LocalGatewayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.queue = MeasurementQueueDB(self.tmp.name + "/queue.db")
        self.gateway = LocalGatewayServer(self.queue, "station-1", "x" * 40, "127.0.0.1", 0)
        self.gateway.start()
        self.base_url = f"http://127.0.0.1:{self.gateway.server.server_address[1]}"

    def tearDown(self):
        self.gateway.close()
        self.tmp.cleanup()

    def test_authentication_idempotency_and_status(self):
        body = json.dumps({"sensor_id": "esp32-aa", "measurement_id": "m-1", "temperature": 12.5}).encode()
        request = Request(self.base_url + "/api/v1/readings", data=body, headers={"X-ESP32-Token": "x" * 40})
        with urlopen(request) as response:
            self.assertEqual(response.status, 202)
        with urlopen(request) as response:
            self.assertEqual(response.status, 200)
        status = json.loads(urlopen(self.base_url + "/api/status").read())
        self.assertEqual(len(self.queue.get_unsent_measurements()), 1)
        self.assertEqual(status["queued_measurements"], 1)
        self.assertTrue(status["sensors"][0]["connected"])

    def test_rejects_wrong_local_token(self):
        request = Request(self.base_url + "/api/v1/readings", data=b"{}", headers={"X-ESP32-Token": "wrong"})
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 401)
        self.assertEqual(self.queue.get_unsent_count(), 0)


if __name__ == "__main__":
    unittest.main()
