"""Validate Home Assistant MQTT discovery offline (no broker needed).

Importing mqtt.py runs under the hardware stubs from tests/__init__, so we can
call send_discovery_messages with a fake client and assert that every expected
entity is announced with a sane config payload.
"""

import json
import unittest


class FakeClient:
    def __init__(self):
        self.published = []

    def publish(self, topic, payload=None, **kwargs):
        self.published.append((topic, payload))


class DiscoveryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import mqtt  # noqa: F401  (imports under stubs)

        cls.mqtt = mqtt

    def test_all_entities_announced(self):
        client = FakeClient()
        self.mqtt.send_discovery_messages(client)
        topics = [t for t, _ in client.published]

        expected_substrings = [
            "homeassistant/light/",  # light + pump
            "_pcb_temp/config",
            "_temperature/config",
            "_humidity/config",
            "_water_level/config",
            "_water_low/config",
            "_water_low_cm/config",
            "_water_low_mode/config",
            "_upper_camera/config",
            "_lower_camera/config",
            "homeassistant/event/",  # button (#78)
            "homeassistant/select/",  # grow stage
            "_grow_stage/config",
            "_grow_day/config",
            "_grow_reminder/config",
            "_grow_start/config",  # start-cycle button
            "_sched_lights/config",  # lights schedule switch
            "_sched_pump/config",  # pump schedule switch
            "_vacation/config",  # vacation mode switch
            "homeassistant/time/",  # everyday on/off/pump times
            "_sched_lights_on/config",
            "_sched_lights_off/config",
            "_sched_lights_brightness/config",
            "_sched_pump_time/config",
            "_sched_pump_duration/config",
        ]
        for sub in expected_substrings:
            self.assertTrue(
                any(sub in t for t in topics),
                f"missing discovery topic containing {sub!r}",
            )

    def test_payloads_are_valid_json_with_device(self):
        client = FakeClient()
        self.mqtt.send_discovery_messages(client)
        for topic, payload in client.published:
            data = json.loads(payload)  # raises if not valid JSON
            self.assertIn("device", data, f"{topic} missing device block")
            self.assertIn("identifiers", data["device"])

    def test_button_event_types(self):
        client = FakeClient()
        self.mqtt.send_discovery_messages(client)
        button = [json.loads(p) for t, p in client.published if "/event/" in t][0]
        self.assertEqual(set(button["event_types"]), {"single", "double", "long"})


if __name__ == "__main__":
    unittest.main()
