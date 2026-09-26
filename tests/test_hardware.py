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


class LowerCameraEnabledTestCase(unittest.TestCase):
    """LOWER_CAMERA_ENABLED is tri-state: unset means the model profile decides."""

    @patch.object(config, "LOWER_CAMERA_ENABLED", None)
    def test_model_profile_decides(self):
        # The 3.0 and the Studio have no lower camera; earlier models do.
        self.assertFalse(hardware.lower_camera_enabled("gardyn 3.0"))
        self.assertFalse(hardware.lower_camera_enabled("gardyn 3.0 (simulated)"))
        self.assertFalse(hardware.lower_camera_enabled("gardyn studio"))
        self.assertTrue(hardware.lower_camera_enabled("gardyn 1.0"))
        self.assertTrue(hardware.lower_camera_enabled("gardyn 2.0"))

    @patch.object(config, "LOWER_CAMERA_ENABLED", None)
    def test_unknown_model_keeps_both_cameras(self):
        self.assertTrue(hardware.lower_camera_enabled("gardyn 4.0"))

    @patch.object(config, "LOWER_CAMERA_ENABLED", True)
    def test_explicit_enable_wins_over_profile(self):
        self.assertTrue(hardware.lower_camera_enabled("gardyn 3.0"))

    @patch.object(config, "LOWER_CAMERA_ENABLED", False)
    def test_explicit_disable_wins_over_profile(self):
        self.assertFalse(hardware.lower_camera_enabled("gardyn studio"))


class SystemRouteTestCase(unittest.TestCase):
    def setUp(self):
        from app import create_app

        self.client = create_app("default").test_client()

    @patch.object(config, "LOWER_CAMERA_ENABLED", None)
    @patch("app.sensors.system.routes.detect_model", return_value="gardyn 3.0")
    def test_system_reports_model_and_profile(self, _model):
        resp = self.client.get("/system")
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["model"], "gardyn 3.0")
        self.assertEqual(body["profile"]["temp_humidity"], "DHT20")
        # Real 3.0 hardware has a single camera, so the profile reports one.
        self.assertIs(body["profile"]["lower_camera"], False)
        self.assertEqual(body["profile"]["cameras"], 1)

    @patch.object(config, "LOWER_CAMERA_ENABLED", None)
    @patch("app.sensors.system.routes.detect_model", return_value="gardyn studio")
    def test_system_reports_one_camera_for_studio(self, _model):
        # The Studio has only the upper camera.
        body = self.client.get("/system").get_json()
        self.assertIs(body["profile"]["lower_camera"], False)
        self.assertEqual(body["profile"]["cameras"], 1)

    @patch.object(config, "LOWER_CAMERA_ENABLED", True)
    @patch("app.sensors.system.routes.detect_model", return_value="gardyn 3.0")
    def test_env_override_reports_two_cameras(self, _model):
        # An explicit LOWER_CAMERA_ENABLED still wins over the model profile.
        body = self.client.get("/system").get_json()
        self.assertIs(body["profile"]["lower_camera"], True)
        self.assertEqual(body["profile"]["cameras"], 2)

    @patch.object(config, "LOWER_CAMERA_ENABLED", None)
    @patch("app.sensors.system.routes.detect_model", return_value="gardyn 3.0 (simulated)")
    def test_profile_resolves_for_suffixed_model(self, _model):
        # Custom/suffixed model strings still resolve to the closest profile.
        body = self.client.get("/system").get_json()
        self.assertEqual(body["profile"]["temp_humidity"], "DHT20")
        self.assertIs(body["profile"]["lower_camera"], False)
        self.assertEqual(body["profile"]["cameras"], 1)


if __name__ == "__main__":
    unittest.main()
