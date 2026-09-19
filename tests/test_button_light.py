"""Physical button single press must toggle based on the light's real state,
not a cached flag, and HA light commands must persist state (offline)."""

import os
import tempfile
import unittest
from unittest.mock import patch


class FakeClient:
    def publish(self, *args, **kwargs):
        pass


class FakeMsg:
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload.encode()


class FakeLight:
    """Stands in for the pigpio-backed light: duty is the 'hardware' level."""

    def __init__(self):
        self.duty = 0

    def set_duty_cycle(self, pct):
        self.duty = pct

    def off(self):
        self.duty = 0

    def get_duty_cycle(self):
        return self.duty


class ButtonLightTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import config
        import mqtt

        cls.mqtt = mqtt
        cls.config = config

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.config.STATE_FILE = os.path.join(self.tmp, "state.json")
        self.light = FakeLight()
        self.client = FakeClient()
        self.patches = [
            patch.object(self.mqtt, "light", self.light),
            patch.object(self.mqtt, "client", self.client, create=True),
            patch.object(self.mqtt, "publish_button_event", lambda e: None),
            patch.object(self.mqtt, "light_state", False),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def send(self, suffix, payload):
        topic = f"{self.mqtt.BASE_TOPIC}/{suffix}"
        self.mqtt.on_message(self.client, None, FakeMsg(topic, payload))

    def test_press_turns_off_light_turned_on_elsewhere(self):
        # e.g. API or schedule turned it on in another process
        self.light.duty = 50
        self.mqtt.handle_single_press()
        self.assertEqual(self.light.duty, 0)

    def test_press_turns_on_when_off(self):
        self.mqtt.handle_single_press()
        self.assertGreater(self.light.duty, 0)

    def test_press_after_ha_on_turns_off(self):
        self.send("light/command", "ON")
        self.mqtt.handle_single_press()
        self.assertEqual(self.light.duty, 0)

    def test_ha_commands_persist_state(self):
        from app.lib import state as state_lib

        self.send("light/command", "ON")
        self.assertTrue(state_lib.load_state().get("light_on"))
        self.send("light/command", "OFF")
        self.assertFalse(state_lib.load_state().get("light_on"))
        self.send("light/brightness/set", "70")
        saved = state_lib.load_state()
        self.assertTrue(saved.get("light_on"))
        self.assertEqual(saved.get("brightness"), 70)

    def test_falls_back_to_cached_state_if_read_fails(self):
        def boom():
            raise RuntimeError("pigpiod down")

        self.light.get_duty_cycle = boom
        self.mqtt.light_state = True
        self.mqtt.handle_single_press()
        self.assertEqual(self.light.duty, 0)


if __name__ == "__main__":
    unittest.main()
