import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import config
from app.lib import grow


class GrowReminderTestCase(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 1, 1, 12, 0, 0)

    def _state(self, days_ago, acknowledged=None):
        started = (self.now - timedelta(days=days_ago)).isoformat()
        return {"stage": "germination", "started": started, "acknowledged": acknowledged or []}

    @patch.object(config, "THINNING_REMINDER_DAYS", 14)
    @patch.object(config, "ROOT_CHECK_REMINDER_DAYS", 21)
    @patch.object(config, "HARVEST_REMINDER_DAYS", 35)
    @patch.object(config, "NUTRIENT_REMINDER_DAYS", 7)
    def test_thinning_due_after_threshold(self):
        due = grow.due_reminders(self._state(15), now=self.now)
        self.assertIn("thinning", due)
        self.assertNotIn("root_check", due)

    @patch.object(config, "THINNING_REMINDER_DAYS", 14)
    @patch.object(config, "NUTRIENT_REMINDER_DAYS", 7)
    def test_nutrient_fires_on_cadence(self):
        due = grow.due_reminders(self._state(14), now=self.now)  # 14 % 7 == 0
        self.assertIn("nutrient", due)

    @patch.object(config, "THINNING_REMINDER_DAYS", 14)
    def test_acknowledged_not_repeated(self):
        state = self._state(15, acknowledged=["thinning"])
        self.assertNotIn("thinning", grow.due_reminders(state, now=self.now))

    def test_set_stage_validates(self):
        with self.assertRaises(ValueError):
            grow.set_stage({}, "bogus")
        self.assertEqual(grow.set_stage({}, "harvest")["stage"], "harvest")

    @patch.object(config, "NUTRIENT_REMINDER_DAYS", 7)
    def test_acknowledge_nutrient_is_per_day(self):
        state = self._state(7)
        grow.acknowledge(state, "nutrient", now=self.now)
        self.assertIn("nutrient_day7", state["acknowledged"])
        self.assertNotIn("nutrient", grow.due_reminders(state, now=self.now))


if __name__ == "__main__":
    unittest.main()
