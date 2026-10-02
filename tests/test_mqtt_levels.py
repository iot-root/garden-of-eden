"""Pump speed and light brightness commands from Home Assistant (offline).

A level is validated before it is stored: an out-of-range value used to be
kept even though the driver rejected it, so every later ON command failed too.
Level 0 means off, and a remembered level of 0 must not turn into an ON that
leaves the device dark or stopped.
"""

import unittest
from unittest import mock

from tests.test_mqtt_control import FakeClient, FakeMsg


class MqttLevelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import config
        import mqtt

        cls.config = config
        cls.mqtt = mqtt
        cls.base = mqtt.BASE_TOPIC

    def setUp(self):
        patches = {
            "pump": mock.MagicMock(),
            "light": mock.MagicMock(),
            "_arm_pump_safety": mock.MagicMock(),
            "_cancel_pump_safety": mock.MagicMock(),
            "WATER_LOW_CM": None,
            "speed": 100,
            "brightness": 50,
        }
        for name, value in patches.items():
            patcher = mock.patch.object(self.mqtt, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.client = FakeClient()

    def send(self, suffix, payload):
        self.mqtt.on_message(self.client, None, FakeMsg(f"{self.base}/{suffix}", payload))

    def published_for(self, suffix):
        topic = f"{self.base}/{suffix}"
        return [p for t, p in self.client.published if t == topic]

    # --- pump ---
    def test_out_of_range_speed_is_ignored_and_not_remembered(self):
        for bad in ("150", "-5", "fast", ""):
            self.send("pump/speed/set", bad)
        self.mqtt.pump.set_speed.assert_not_called()
        self.assertEqual(self.mqtt.speed, 100)

        self.send("pump/command", "ON")
        self.mqtt.pump.set_speed.assert_called_once_with(100)
        self.assertEqual(self.published_for("pump/state"), ["ON"])

    def test_speed_zero_turns_pump_off_and_keeps_last_speed(self):
        self.send("pump/speed/set", "40")
        self.send("pump/speed/set", "0")
        self.mqtt.pump.off.assert_called_once()
        self.mqtt._cancel_pump_safety.assert_called_once()
        self.assertEqual(self.published_for("pump/state"), ["ON", "OFF"])

        self.send("pump/command", "ON")
        self.mqtt.pump.set_speed.assert_called_with(40)

    def test_speed_set_reports_pump_on(self):
        self.send("pump/speed/set", "60")
        self.mqtt.pump.set_speed.assert_called_once_with(60)
        self.mqtt._arm_pump_safety.assert_called_once()
        self.assertEqual(self.published_for("pump/state"), ["ON"])
        self.assertEqual(self.published_for("pump/speed/state"), ["60"])

    def test_on_with_remembered_zero_speed_uses_default(self):
        self.mqtt.speed = 0  # e.g. restored after a REST speed of 0
        self.send("pump/command", "ON")
        self.mqtt.pump.set_speed.assert_called_once_with(self.config.DEFAULT_PUMP_SPEED)
        self.assertEqual(
            self.published_for("pump/speed/state"), [str(self.config.DEFAULT_PUMP_SPEED)]
        )

    # --- light ---
    def test_out_of_range_brightness_is_ignored_and_not_remembered(self):
        self.send("light/brightness/set", "101")
        self.mqtt.light.set_duty_cycle.assert_not_called()
        self.assertEqual(self.mqtt.brightness, 50)

        self.send("light/command", "ON")
        self.mqtt.light.set_duty_cycle.assert_called_once_with(50)

    def test_brightness_zero_turns_light_off_and_keeps_last_level(self):
        self.send("light/brightness/set", "70")
        self.send("light/brightness/set", "0")
        self.mqtt.light.off.assert_called_once()
        self.assertEqual(self.published_for("light/state"), ["ON", "OFF"])

        self.send("light/command", "ON")
        self.mqtt.light.set_duty_cycle.assert_called_with(70)

    def test_on_with_remembered_zero_brightness_uses_default(self):
        self.mqtt.brightness = 0
        self.send("light/command", "ON")
        self.mqtt.light.set_duty_cycle.assert_called_once_with(self.config.DEFAULT_BRIGHTNESS)


if __name__ == "__main__":
    unittest.main()
