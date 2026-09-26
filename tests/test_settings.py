"""Web-UI model selection, persisted outside .env by app/lib/settings.py."""

import json
import os
import tempfile
import unittest
from unittest import mock

import config
from app import create_app
from app.lib import settings
from app.lib.hardware import detect_model


class SettingsTestCase(unittest.TestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".json")
        os.close(handle)
        os.unlink(self.path)  # start with no stored choice
        self.patch = mock.patch.object(config, "HARDWARE_FILE", self.path)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_no_override_by_default(self):
        self.assertIsNone(settings.get_model_override())

    def test_set_then_read_back(self):
        settings.set_model_override("gardyn studio")
        self.assertEqual(settings.get_model_override(), "gardyn studio")

    def test_auto_clears_the_override(self):
        settings.set_model_override("gardyn studio")
        settings.set_model_override("auto")
        self.assertIsNone(settings.get_model_override())

    def test_empty_name_clears_the_override(self):
        settings.set_model_override("gardyn studio")
        settings.set_model_override("")
        self.assertIsNone(settings.get_model_override())

    def test_unknown_model_is_rejected(self):
        # A typo must not be able to point the unit at a model that is not real.
        with self.assertRaises(ValueError):
            settings.set_model_override("gardyn 9.0")

    def test_rejected_model_is_not_persisted(self):
        with self.assertRaises(ValueError):
            settings.set_model_override("gardyn 9.0")
        self.assertIsNone(settings.get_model_override())

    def test_corrupt_file_is_treated_as_no_override(self):
        with open(self.path, "w") as fh:
            fh.write("{not json")
        self.assertIsNone(settings.get_model_override())

    def test_stored_file_is_valid_json(self):
        settings.set_model_override("gardyn studio")
        with open(self.path) as fh:
            self.assertEqual(json.load(fh)["model"], "gardyn studio")

    def test_available_models_includes_auto(self):
        models = settings.available_models()
        self.assertIn("auto", models)
        self.assertIn("gardyn studio", models)


class PrecedenceTestCase(unittest.TestCase):
    """UI choice beats .env, which beats sensor inference."""

    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".json")
        os.close(handle)
        os.unlink(self.path)
        p = mock.patch.object(config, "HARDWARE_FILE", self.path)
        p.start()
        self.addCleanup(p.stop)

    def test_settings_choice_beats_the_environment(self):
        with mock.patch.object(config, "MODEL_OVERRIDE", "gardyn 1.0"):
            settings.set_model_override("gardyn studio")
            self.assertEqual(detect_model(), "gardyn studio")
            self.assertEqual(settings.describe_source(), "settings")

    def test_environment_used_when_no_ui_choice(self):
        with mock.patch.object(config, "MODEL_OVERRIDE", "gardyn 1.0"):
            self.assertEqual(detect_model(), "gardyn 1.0")
            self.assertEqual(settings.describe_source(), "environment")

    def test_clearing_returns_to_the_environment(self):
        with mock.patch.object(config, "MODEL_OVERRIDE", "gardyn 1.0"):
            settings.set_model_override("gardyn studio")
            settings.set_model_override("auto")
            self.assertEqual(detect_model(), "gardyn 1.0")

    def test_auto_is_inferred_when_nothing_is_set(self):
        with (
            mock.patch.object(config, "MODEL_OVERRIDE", ""),
            mock.patch("app.lib.hardware.i2c_device_present", return_value=True),
        ):
            self.assertEqual(settings.describe_source(), "auto")


class ModelRouteTestCase(unittest.TestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".json")
        os.close(handle)
        os.unlink(self.path)
        p = mock.patch.object(config, "HARDWARE_FILE", self.path)
        p.start()
        self.addCleanup(p.stop)
        app = create_app("default")
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_get_reports_the_model_fields(self):
        body = self.client.get("/system").get_json()
        for key in ("model", "model_source", "model_override", "available_models"):
            self.assertIn(key, body)
        self.assertIn("auto", body["available_models"])

    def test_post_sets_the_model(self):
        r = self.client.post("/system/model", json={"model": "gardyn studio"})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["applied_model"], "gardyn studio")
        self.assertEqual(body["model_source"], "settings")

    def test_post_auto_clears(self):
        self.client.post("/system/model", json={"model": "gardyn studio"})
        r = self.client.post("/system/model", json={"model": "auto"})
        self.assertIsNone(r.get_json()["applied_model"])

    def test_post_unknown_model_is_400(self):
        r = self.client.post("/system/model", json={"model": "gardyn 9.0"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("unknown model", r.get_json()["error"])

    def test_post_is_covered_by_admin_auth(self):
        # Must not be a way around the admin password.
        app = create_app("default")
        app.config["TESTING"] = True
        c = app.test_client()
        r = c.post(
            "/system/model",
            json={"model": "gardyn studio"},
            environ_base={"REMOTE_ADDR": "203.0.113.9"},
        )
        self.assertEqual(r.status_code, 401)


if __name__ == "__main__":
    unittest.main()
