import unittest
from unittest.mock import patch

import config
from app.lib import hardware


class DetectModelTestCase(unittest.TestCase):
    @patch.object(config, "MODEL_OVERRIDE", "gardyn studio")
    def test_override_wins(self):
        self.assertEqual(hardware.detect_model(), "gardyn studio")

    @patch.object(config, "MODEL_OVERRIDE", None)
    @patch.object(config, "SENSOR_TYPE", "DHT20")
    @patch.object(hardware, "i2c_device_present", return_value=False)
    def test_dht20_implies_3_0(self, _present):
        self.assertEqual(hardware.detect_model(), "gardyn 3.0")

    @patch.object(config, "MODEL_OVERRIDE", None)
    @patch.object(config, "SENSOR_TYPE", "AM2320")
    @patch.object(hardware, "i2c_device_present", return_value=False)
    def test_am2320_implies_2_0(self, _present):
        self.assertEqual(hardware.detect_model(), "gardyn 2.0")


class SystemRouteTestCase(unittest.TestCase):
    def setUp(self):
        from app import create_app

        self.client = create_app("default").test_client()

    @patch("app.sensors.system.routes.detect_model", return_value="gardyn 3.0")
    def test_system_reports_model_and_profile(self, _model):
        resp = self.client.get("/system")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["model"], "gardyn 3.0")
        self.assertEqual(body["profile"], config.MODELS["gardyn 3.0"])

    @patch("app.sensors.system.routes.detect_model", return_value="gardyn 3.0 (simulated)")
    def test_profile_resolves_for_suffixed_model(self, _model):
        # Custom/suffixed model strings still resolve to the closest profile.
        body = self.client.get("/system").get_json()
        self.assertEqual(body["profile"], config.MODELS["gardyn 3.0"])


if __name__ == "__main__":
    unittest.main()
