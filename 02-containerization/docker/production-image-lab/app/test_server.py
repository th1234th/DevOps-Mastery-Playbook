import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

from server import Handler


class ServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_root_returns_service_metadata(self):
        with urlopen(self.base_url + "/") as response:
            body = json.load(response)
        self.assertEqual(body["service"], "image-lab")
        self.assertEqual(body["version"], "1.0.0")

    def test_health_endpoint_is_successful(self):
        with urlopen(self.base_url + "/healthz") as response:
            self.assertEqual(response.read(), b"ok\n")

    def test_unknown_route_is_not_found(self):
        try:
            urlopen(self.base_url + "/not-a-route")
        except HTTPError as error:
            self.assertEqual(error.code, 404)
            error.close()
        else:
            self.fail("unknown route should return HTTP 404")


if __name__ == "__main__":
    unittest.main()