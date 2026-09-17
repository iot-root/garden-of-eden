import unittest

from flask import Flask, jsonify

from app.lib.lib import check_sensor_guard, parse_level


class CheckSensorGuardTestCase(unittest.TestCase):
    def _make_client(self, sensor, handler):
        app = Flask(__name__)
        guard = check_sensor_guard(sensor=sensor, sensor_name="Widget")
        app.add_url_rule("/x", "x", guard(handler))
        return app.test_client()

    def test_uninitialized_sensor_returns_400(self):
        client = self._make_client(None, lambda: jsonify(ok=True))
        resp = client.get("/x")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("not initialized", resp.get_json()["error"])

    def test_hardware_error_returns_503(self):
        def boom():
            raise RuntimeError("i2c bus error")

        client = self._make_client(object(), boom)
        resp = client.get("/x")
        self.assertEqual(resp.status_code, 503)
        self.assertIn("hardware unavailable", resp.get_json()["error"])

    def test_value_error_returns_400(self):
        def bad():
            raise ValueError("must be 0-100")

        client = self._make_client(object(), bad)
        resp = client.get("/x")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.get_json()["error"], "must be 0-100")

    def test_happy_path_passes_through(self):
        client = self._make_client(object(), lambda: (jsonify(ok=True), 200))
        resp = client.get("/x")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()["ok"])


class ParseLevelTestCase(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(parse_level({"value": 50}), 50)

    def test_default_when_missing(self):
        self.assertEqual(parse_level({}, default=70), 70)

    def test_rejects_non_numeric(self):
        with self.assertRaises(ValueError):
            parse_level({"value": "loud"})

    def test_rejects_bool(self):
        with self.assertRaises(ValueError):
            parse_level({"value": True})

    def test_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            parse_level({"value": 150})
        with self.assertRaises(ValueError):
            parse_level({"value": -1})


if __name__ == "__main__":
    unittest.main()
