import unittest
from unittest.mock import patch

import config
from app import create_app


class PumpRunTestCase(unittest.TestCase):
    def setUp(self):
        self.client = create_app("default").test_client()

    @patch("app.sensors.pump.routes.threading.Timer")
    @patch("app.sensors.pump.routes.pump_control.on")
    def test_run_starts_pump_and_schedules_off(self, mock_on, mock_timer):
        resp = self.client.post("/pump/run", json={"seconds": 120})
        self.assertEqual(resp.status_code, 200)
        mock_on.assert_called_once()
        mock_timer.assert_called_once()  # off scheduled on a timer
        self.assertEqual(mock_timer.call_args[0][0], 120)

    def test_run_rejects_out_of_range(self):
        self.assertEqual(self.client.post("/pump/run", json={"seconds": 0}).status_code, 400)
        self.assertEqual(self.client.post("/pump/run", json={"seconds": 99999}).status_code, 400)

    @patch("app.sensors.pump.routes.threading.Timer")
    @patch("app.sensors.pump.routes.pump_control.on")
    def test_run_rejects_above_safety_cap(self, mock_on, mock_timer):
        # The cap itself is allowed; one second over is rejected.
        ok = self.client.post("/pump/run", json={"seconds": config.MAX_PUMP_RUN_SECONDS})
        self.assertEqual(ok.status_code, 200)
        over = self.client.post("/pump/run", json={"seconds": config.MAX_PUMP_RUN_SECONDS + 1})
        self.assertEqual(over.status_code, 400)

    @patch("app.sensors.pump.routes.threading.Timer")
    @patch("app.sensors.pump.routes.pump_control.on")
    def test_on_arms_safety_auto_off(self, mock_on, mock_timer):
        resp = self.client.post("/pump/on")
        self.assertEqual(resp.status_code, 200)
        mock_on.assert_called_once()
        mock_timer.assert_called_once()  # auto-off armed even with no /run
        self.assertEqual(mock_timer.call_args[0][0], config.MAX_PUMP_RUN_SECONDS)


if __name__ == "__main__":
    unittest.main()
