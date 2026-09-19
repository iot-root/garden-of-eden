"""Smoke-test every GET surface through the app: nothing should throw a 500.

Sensor endpoints may legitimately return 503 (hardware unavailable) under stub
hardware — that's the guard working, not a crash. We assert no endpoint returns
an unhandled 500 and that the web UI + system endpoints work.
"""

import unittest

from app import create_app


class SurfaceSmokeTestCase(unittest.TestCase):
    def setUp(self):
        self.client = create_app("default").test_client()

    def test_no_get_route_returns_500(self):
        for rule in self.client.application.url_map.iter_rules():
            if "GET" not in rule.methods:
                continue
            if "<" in rule.rule:  # skip parameterized routes
                continue
            resp = self.client.get(rule.rule)
            self.assertNotEqual(
                resp.status_code,
                500,
                f"{rule.rule} returned an unhandled 500",
            )

    def test_web_ui_and_system_ok(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/system").status_code, 200)
        self.assertEqual(self.client.get("/grow").status_code, 200)
        self.assertEqual(self.client.get("/schedule").status_code, 200)

    def test_bad_json_body_is_400_not_500(self):
        # Malformed/non-numeric input must be a clean 4xx, never a 500.
        r = self.client.post("/light/brightness", json={"value": "loud"})
        self.assertEqual(r.status_code, 400)
        r = self.client.post("/pump/speed", json={"value": 999})
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
