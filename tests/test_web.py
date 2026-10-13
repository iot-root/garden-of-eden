import unittest

from app import create_app
from app.web.routes import ICON_PATHS


class WebUITestCase(unittest.TestCase):
    def setUp(self):
        self.client = create_app("default").test_client()

    def test_root_serves_html(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.content_type)
        self.assertIn(b"Garden of Eden", resp.data)

    def test_icons_served_from_site_root(self):
        expected = {
            "/favicon.ico": "image/",
            "/favicon.svg": "image/svg+xml",
            "/apple-touch-icon.png": "image/png",
            "/apple-touch-icon-precomposed.png": "image/png",
            "/icon-192.png": "image/png",
            "/icon-512.png": "image/png",
            "/site.webmanifest": "application/manifest+json",
        }
        self.assertEqual(set(expected), set(ICON_PATHS))
        for path, content_type in expected.items():
            with self.subTest(path=path), self.client.get(path) as resp:
                self.assertEqual(resp.status_code, 200)
                self.assertIn(content_type, resp.content_type)
                self.assertTrue(resp.data)

    def test_page_links_icons(self):
        with self.client.get("/") as resp:
            html = resp.data
        self.assertNotIn(b'href="data:image', html)
        for href in (b"/favicon.ico", b"/apple-touch-icon.png", b"/site.webmanifest"):
            self.assertIn(b'href="' + href + b'"', html)


if __name__ == "__main__":
    unittest.main()
