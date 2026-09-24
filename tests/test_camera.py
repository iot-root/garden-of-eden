import unittest
from unittest.mock import patch

import config
from app import create_app


class CameraRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("default")
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    @patch("app.sensors.camera.routes.camera.capture_upper")
    def test_capture_failure_returns_503(self, mock_capture):
        mock_capture.side_effect = FileNotFoundError("fswebcam missing")
        resp = self.client.get("/camera/upper")
        self.assertEqual(resp.status_code, 503)

    @patch("app.sensors.camera.routes.send_file")
    @patch("app.sensors.camera.routes.camera.capture_lower")
    def test_capture_success_serves_file(self, mock_capture, mock_send_file):
        with patch.object(config, "LOWER_CAMERA_ENABLED", True):
            mock_send_file.return_value = "IMG"
            resp = self.client.get("/camera/lower")
            mock_capture.assert_called_once()
            self.assertEqual(resp.status_code, 200)

    @patch.object(config, "LOWER_CAMERA_ENABLED", False)
    def test_disabled_lower_camera_returns_not_found(self):
        resp = self.client.get("/camera/lower")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
