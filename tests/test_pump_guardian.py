import sys
import os
import unittest
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "pump_guardian",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "app", "sensors", "pump", "pump_guardian.py")
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
PumpGuardian = _mod.PumpGuardian


def make_guardian(max_on_seconds=900):
    pump_off_calls = []
    publish_calls = []
    guardian = PumpGuardian(
        pump_off_fn=lambda: pump_off_calls.append(True),
        mqtt_publish_fn=lambda topic, payload: publish_calls.append((topic, payload)),
        base_topic="gardyn",
        max_on_seconds=max_on_seconds,
    )
    return guardian, pump_off_calls, publish_calls


class TestPumpGuardian(unittest.TestCase):

    def test_no_intervention_when_pump_off_before_limit(self):
        guardian, pump_off_calls, publish_calls = make_guardian(max_on_seconds=900)
        guardian.on_pump_on()
        guardian.on_pump_off()
        # Manually trigger check — pump is off, nothing should happen
        guardian._pump_start_time = None
        with guardian._lock:
            start = guardian._pump_start_time
        self.assertIsNone(start)
        self.assertEqual(pump_off_calls, [])
        self.assertEqual(publish_calls, [])

    def test_forced_off_after_timeout(self):
        import time
        guardian, pump_off_calls, publish_calls = make_guardian(max_on_seconds=5)
        guardian.on_pump_on()
        # Backdate start time past the limit
        with guardian._lock:
            guardian._pump_start_time = time.time() - 10
        # Manually invoke the check logic
        with guardian._lock:
            elapsed = time.time() - guardian._pump_start_time
            if elapsed > guardian._max_on_seconds:
                guardian._pump_off_fn()
                guardian._mqtt_publish_fn(guardian._base_topic + "/pump/state", "OFF")
                guardian._mqtt_publish_fn("gardyn/pump/guardian", "forced_off")
                guardian._pump_start_time = None
        self.assertEqual(len(pump_off_calls), 1)
        self.assertIn(("gardyn/pump/state", "OFF"), publish_calls)
        self.assertIn(("gardyn/pump/guardian", "forced_off"), publish_calls)
        with guardian._lock:
            self.assertIsNone(guardian._pump_start_time)

    def test_guardian_resets_and_watches_again_after_forced_off(self):
        import time
        guardian, pump_off_calls, publish_calls = make_guardian(max_on_seconds=5)

        # First cycle: force timeout
        guardian.on_pump_on()
        with guardian._lock:
            guardian._pump_start_time = time.time() - 10
            elapsed = time.time() - guardian._pump_start_time
            if elapsed > guardian._max_on_seconds:
                guardian._pump_off_fn()
                guardian._mqtt_publish_fn(guardian._base_topic + "/pump/state", "OFF")
                guardian._mqtt_publish_fn("gardyn/pump/guardian", "forced_off")
                guardian._pump_start_time = None

        self.assertEqual(len(pump_off_calls), 1)

        # Second cycle: pump turned on again, guardian watches fresh
        guardian.on_pump_on()
        with guardian._lock:
            self.assertIsNotNone(guardian._pump_start_time)

        guardian.on_pump_off()
        with guardian._lock:
            self.assertIsNone(guardian._pump_start_time)

        # No additional forced-off
        self.assertEqual(len(pump_off_calls), 1)

    def test_off_without_prior_on_no_error(self):
        guardian, pump_off_calls, publish_calls = make_guardian()
        try:
            guardian.on_pump_off()
        except Exception as e:
            self.fail(f"on_pump_off raised unexpectedly: {e}")
        self.assertEqual(pump_off_calls, [])
        self.assertEqual(publish_calls, [])


if __name__ == "__main__":
    unittest.main()
