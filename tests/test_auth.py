"""API-key auth (issue #7). Auth only activates when GARDEN_API_KEY is set;
localhost and the public UI/health paths always bypass it.
"""

import unittest
from unittest.mock import patch

import config
from app import create_app

REMOTE = {"REMOTE_ADDR": "203.0.113.9"}  # a non-localhost client


def _client():
    app = create_app("default")
    app.config["TESTING"] = True
    return app.test_client()


class AuthDisabledTestCase(unittest.TestCase):
    @patch.object(config, "GARDEN_API_KEY", "")
    def test_no_key_means_open(self):
        # With no key configured, remote requests are not challenged.
        self.assertEqual(_client().get("/system", environ_base=REMOTE).status_code, 200)


class AuthEnabledTestCase(unittest.TestCase):
    @patch.object(config, "GARDEN_API_KEY", "s3cret")
    def test_remote_without_key_is_401(self):
        self.assertEqual(_client().get("/system", environ_base=REMOTE).status_code, 401)

    @patch.object(config, "GARDEN_API_KEY", "s3cret")
    def test_remote_with_wrong_key_is_401(self):
        r = _client().get("/system", headers={"X-API-Key": "nope"}, environ_base=REMOTE)
        self.assertEqual(r.status_code, 401)

    @patch.object(config, "GARDEN_API_KEY", "s3cret")
    def test_remote_with_correct_key_ok(self):
        r = _client().get("/system", headers={"X-API-Key": "s3cret"}, environ_base=REMOTE)
        self.assertEqual(r.status_code, 200)

    @patch.object(config, "GARDEN_API_KEY", "s3cret")
    def test_localhost_bypasses_auth(self):
        # Default test client REMOTE_ADDR is 127.0.0.1 -> cron/local bypass.
        self.assertEqual(_client().get("/system").status_code, 200)

    @patch.object(config, "GARDEN_API_KEY", "s3cret")
    def test_public_paths_open_without_key(self):
        c = _client()
        self.assertEqual(c.get("/", environ_base=REMOTE).status_code, 200)
        self.assertEqual(c.get("/health", environ_base=REMOTE).status_code, 200)


if __name__ == "__main__":
    unittest.main()
