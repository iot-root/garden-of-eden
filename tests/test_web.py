import unittest

from app import create_app


class WebUITestCase(unittest.TestCase):
    def setUp(self):
        self.client = create_app("default").test_client()

    def test_root_serves_html(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.content_type)
        self.assertIn(b"Garden of Eden", resp.data)


if __name__ == "__main__":
    unittest.main()
