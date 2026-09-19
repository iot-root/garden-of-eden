import json
import os
import tempfile
import unittest
from unittest.mock import patch

import config
from app.lib import state


class ActuatorStateTestCase(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.unlink(self.path)  # start absent
        self._patch = patch.object(config, "STATE_FILE", self.path)
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_defaults_when_absent(self):
        s = state.load_state()
        self.assertFalse(s["light_on"])
        self.assertFalse(s["pump_on"])

    def test_save_and_reload_roundtrip(self):
        state.save_state(light_on=True, brightness=42)
        s = state.load_state()
        self.assertTrue(s["light_on"])
        self.assertEqual(s["brightness"], 42)
        # File is valid JSON on disk.
        with open(self.path) as fh:
            self.assertEqual(json.load(fh)["brightness"], 42)

    def test_partial_update_preserves_other_fields(self):
        state.save_state(pump_on=True, speed=80)
        state.save_state(light_on=True)
        s = state.load_state()
        self.assertTrue(s["pump_on"])
        self.assertEqual(s["speed"], 80)
        self.assertTrue(s["light_on"])


if __name__ == "__main__":
    unittest.main()
