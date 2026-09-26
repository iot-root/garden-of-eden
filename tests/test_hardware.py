import os
import tempfile
import unittest
from unittest.mock import patch

import config
from app.lib import hardware


class _NoStoredModelMixin:
    """Isolate from the operator's real ~/.garden_hardware.json.

    detect_model() reads the web-UI override from disk, so without this the
    suite would depend on whatever the running Pi last selected and pass or
    fail depending on the machine it runs on.
    """

    def setUp(self):
        handle, self.hardware_path = tempfile.mkstemp(suffix=".json")
        os.close(handle)
        os.unlink(self.hardware_path)  # no stored choice
        patcher = patch.object(config, "HARDWARE_FILE", self.hardware_path)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._remove_hardware_file)

    def _remove_hardware_file(self):
        if os.path.exists(self.hardware_path):
            os.unlink(self.hardware_path)


class DetectModelTestCase(_NoStoredModelMixin, unittest.TestCase):
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

    def test_a_stored_choice_beats_inference_and_the_environment(self):
        # The web-UI override is the top of the precedence chain, and it is
        # read from disk rather than from the environment.
        from app.lib import settings

        settings.set_model_override("gardyn studio")
        with (
            patch.object(config, "MODEL_OVERRIDE", "gardyn 1.0"),
            patch.object(config, "SENSOR_TYPE", "DHT20"),
            patch.object(hardware, "i2c_device_present", return_value=True),
        ):
            self.assertEqual(hardware.detect_model(), "gardyn studio")
        self.assertEqual(settings.describe_source(), "settings")


class LowerCameraEnabledTestCase(unittest.TestCase):
    """LOWER_CAMERA_ENABLED is tri-state: unset means the model profile decides."""

    @patch.object(config, "LOWER_CAMERA_ENABLED", None)
    def test_model_profile_decides(self):
        # The Studio line has no lower camera; the Home line does.
        self.assertFalse(hardware.lower_camera_enabled("gardyn studio"))
        self.assertFalse(hardware.lower_camera_enabled("gardyn studio 2"))
        self.assertTrue(hardware.lower_camera_enabled("gardyn 1.0"))
        self.assertTrue(hardware.lower_camera_enabled("gardyn 2.0"))
        self.assertTrue(hardware.lower_camera_enabled("gardyn 3.0"))
        self.assertTrue(hardware.lower_camera_enabled("gardyn 3.0 (simulated)"))

    @patch.object(config, "POD_COUNT", 0)
    @patch.object(config, "POD_COLUMNS", 0)
    def test_pod_geometry_follows_the_model(self):
        # With nothing in .env, the model profile decides both numbers.
        self.assertEqual(hardware.pod_capacity("gardyn studio"), 16)
        self.assertEqual(hardware.tower_count("gardyn studio"), 2)
        self.assertEqual(hardware.pod_capacity("gardyn 3.0"), 30)
        self.assertEqual(hardware.tower_count("gardyn 3.0"), 3)

    @patch.object(config, "POD_COUNT", 12)
    @patch.object(config, "POD_COLUMNS", 4)
    def test_env_overrides_pod_geometry(self):
        # An explicit .env value wins for a unit that differs from its profile.
        self.assertEqual(hardware.pod_capacity("gardyn studio"), 12)
        self.assertEqual(hardware.tower_count("gardyn studio"), 4)

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
        # The 3.0 is a Home-line unit, so it has both cameras.
        self.assertIs(body["profile"]["lower_camera"], True)
        self.assertEqual(body["profile"]["cameras"], 2)
        # ...and the Home line's physical layout.
        self.assertEqual(body["profile"]["towers"], 3)
        self.assertEqual(body["profile"]["light_bars"], 2)
        self.assertEqual(body["profile"]["pods"], 30)

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
        self.assertIs(body["profile"]["lower_camera"], True)
        self.assertEqual(body["profile"]["cameras"], 2)


if __name__ == "__main__":
    unittest.main()
