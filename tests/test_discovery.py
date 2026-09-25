"""Validate Home Assistant MQTT discovery offline (no broker needed).

Importing mqtt.py runs under the hardware stubs from tests/__init__, so we can
call send_discovery_messages with a fake client and assert that every expected
entity is announced with a sane config payload.
"""

import json
import unittest
from unittest.mock import patch


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

    def setUp(self):
        # The lower camera is optional (LOWER_CAMERA_ENABLED). A local .env may
        # disable it, so force it on here and assert the full entity set
        # regardless of the host's configuration.
        patcher = patch.object(self.mqtt, "LOWER_CAMERA_ENABLED", True)
        patcher.start()
        self.addCleanup(patcher.stop)

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

    def test_every_entity_has_a_matching_unique_id(self):
        # The ent() helper is the single place unique_id is generated. If its
        # `obj` argument ever disagreed with the entity it describes, Home
        # Assistant would silently orphan the entity and re-create it under a
        # new id, leaving the old one behind as unavailable. Tie the two
        # together: the config topic is
        # homeassistant/<component>/gardyn/<unique_id>/config.
        client = FakeClient()
        self.mqtt.send_discovery_messages(client)
        seen = set()
        for topic, payload in client.published:
            data = json.loads(payload)
            unique_id = data.get("unique_id")
            self.assertTrue(unique_id, f"{topic} missing unique_id")
            self.assertEqual(
                unique_id,
                topic.split("/")[-2],
                f"{topic} unique_id does not match its config topic",
            )
            self.assertNotIn(unique_id, seen, f"duplicate unique_id {unique_id!r}")
            seen.add(unique_id)

    def test_button_event_types(self):
        client = FakeClient()
        self.mqtt.send_discovery_messages(client)
        button = [json.loads(p) for t, p in client.published if "/event/" in t][0]
        self.assertEqual(set(button["event_types"]), {"single", "double", "long"})

    def test_lower_camera_omitted_when_disabled(self):
        client = FakeClient()
        with patch.object(self.mqtt, "LOWER_CAMERA_ENABLED", False):
            self.mqtt.send_discovery_messages(client)
        topics = [t for t, _ in client.published]
        self.assertTrue(any("_upper_camera/config" in t for t in topics))
        self.assertFalse(any("_lower_camera/config" in t for t in topics))


if __name__ == "__main__":
    unittest.main()
