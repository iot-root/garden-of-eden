import os
import tempfile
import unittest
from unittest.mock import patch

from app import create_app
from app.sensors.camera import camera


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

    @patch("app.sensors.camera.routes.camera.capture_upper")
    def test_camera_error_returns_503(self, mock_capture):
        # fswebcam exits 0 with the camera unplugged; the route must not 500.
        mock_capture.side_effect = camera.CameraError("wrote no image")
        resp = self.client.get("/camera/upper")
        self.assertEqual(resp.status_code, 503)

    @patch("app.sensors.camera.routes.send_file")
    @patch("app.sensors.camera.routes.camera.capture_lower")
    def test_capture_success_serves_file(self, mock_capture, mock_send_file):
        mock_send_file.return_value = "IMG"
        resp = self.client.get("/camera/lower")
        mock_capture.assert_called_once()
        self.assertEqual(resp.status_code, 200)


class CaptureTestCase(unittest.TestCase):
    """fswebcam exits 0 when the device is missing and writes nothing, so
    capture() has to judge the result by the image it produced."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "cam.jpg")

    @patch("app.sensors.camera.camera.subprocess.run")
    def test_raises_when_no_image_is_written(self, mock_run):
        mock_run.return_value.stderr = b"stat: No such file or directory"
        with self.assertRaises(camera.CameraError):
            camera.capture("/dev/video0", self.path)

    @patch("app.sensors.camera.camera.subprocess.run")
    def test_raises_when_the_image_is_empty(self, mock_run):
        def write_nothing(*args, **kwargs):
            open(self.path, "wb").close()
            mock_run.stderr = b""
            return mock_run

        mock_run.side_effect = write_nothing
        with self.assertRaises(camera.CameraError):
            camera.capture("/dev/video0", self.path)

    @patch("app.sensors.camera.camera.subprocess.run")
    def test_stale_image_from_an_earlier_capture_is_not_reused(self, mock_run):
        with open(self.path, "wb") as fh:
            fh.write(b"old frame")
        mock_run.return_value.stderr = b""
        with self.assertRaises(camera.CameraError):
            camera.capture("/dev/video0", self.path)
        self.assertFalse(os.path.exists(self.path))

    @patch("app.sensors.camera.camera.subprocess.run")
    def test_returns_the_path_when_an_image_is_written(self, mock_run):
        def write_frame(*args, **kwargs):
            with open(self.path, "wb") as fh:
                fh.write(b"\xff\xd8jpeg")
            return mock_run

        mock_run.side_effect = write_frame
        self.assertEqual(camera.capture("/dev/video0", self.path), self.path)


if __name__ == "__main__":
    unittest.main()
