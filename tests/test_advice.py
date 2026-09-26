"""Claude advice integration (issue #101).

The Anthropic SDK is never installed in the test environment and is never
called: ``_client`` is patched. These tests cover snapshot assembly, the
disabled path, the image block, and the route's status codes.
"""

import contextlib
import json
import os
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

import config
from app import create_app
from app.integrations import claude


@contextlib.contextmanager
def _fake_anthropic():
    """Inject a stub ``anthropic`` module.

    The SDK is not a test dependency (requirements-dev.txt is pure-Python and
    the integration imports it lazily), so tests that reach ``_client()``
    supply a stand-in and assert on how it was constructed.
    """
    mod = types.ModuleType("anthropic")
    mock_cls = MagicMock(name="Anthropic")
    mod.Anthropic = mock_cls
    with patch.dict(sys.modules, {"anthropic": mod}):
        yield mock_cls


def _response(text="Looks healthy.", in_tokens=1234, out_tokens=56):
    """A stand-in for anthropic.types.Message."""
    block = MagicMock()
    block.type = "text"
    block.text = text
    usage = MagicMock()
    usage.input_tokens = in_tokens
    usage.output_tokens = out_tokens
    msg = MagicMock()
    msg.content = [block]
    msg.usage = usage
    return msg


class IsEnabledTestCase(unittest.TestCase):
    @patch.object(config, "ANTHROPIC_API_KEY", "")
    def test_disabled_without_key(self):
        self.assertFalse(claude.is_enabled())

    @patch.object(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    def test_enabled_with_key(self):
        self.assertTrue(claude.is_enabled())


class PerRequestKeyTestCase(unittest.TestCase):
    """The browser supplies the Claude key per request (X-Claude-Key)."""

    @patch.object(config, "ANTHROPIC_API_KEY", "")
    def test_request_key_enables_with_no_server_key(self):
        self.assertFalse(claude.is_enabled())
        self.assertTrue(claude.is_enabled("sk-ant-from-browser"))

    @patch.object(config, "ANTHROPIC_API_KEY", "sk-ant-server")
    def test_server_key_still_works(self):
        self.assertTrue(claude.is_enabled())
        self.assertTrue(claude.is_enabled("sk-ant-from-browser"))

    @patch.object(config, "ANTHROPIC_API_KEY", "sk-ant-server")
    def test_whitespace_only_request_key_falls_back(self):
        # A blank header must not count as a supplied key.
        self.assertTrue(claude.is_enabled("   "))

    @patch.object(config, "ANTHROPIC_API_KEY", "")
    def test_client_prefers_the_request_key(self):
        with _fake_anthropic() as mock_cls:
            claude._client("sk-ant-from-browser")
        self.assertEqual(mock_cls.call_args.kwargs["api_key"], "sk-ant-from-browser")

    @patch.object(config, "ANTHROPIC_API_KEY", "sk-ant-server")
    def test_client_falls_back_to_server_key(self):
        with _fake_anthropic() as mock_cls:
            claude._client("")
        self.assertEqual(mock_cls.call_args.kwargs["api_key"], "sk-ant-server")


class SnapshotTestCase(unittest.TestCase):
    def test_snapshot_has_expected_keys(self):
        state = claude.snapshot()
        for key in (
            "model",
            "profile",
            "air_temperature_c",
            "humidity_percent",
            "pcb_temperature_c",
            "water_distance_cm",
            "water_low",
            "actuators",
            "grow",
        ):
            self.assertIn(key, state)

    def test_snapshot_degrades_when_sensors_fail(self):
        # A dead sensor must degrade to null, not explode the whole request.
        with patch.object(claude, "_read", side_effect=lambda label, fn: None):
            state = claude.snapshot()
        self.assertIsNone(state["air_temperature_c"])
        self.assertIsNone(state["humidity_percent"])
        self.assertIsNone(state["pcb_temperature_c"])

    def test_days_since_handles_garbage(self):
        self.assertIsNone(claude._days_since("not-a-date"))
        self.assertIsNone(claude._days_since(None))


class BuildContentTestCase(unittest.TestCase):
    def test_image_block_precedes_text(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as fh:
            fh.write(b"\xff\xd8\xff\xd9fake-jpeg")
            path = fh.name
        self.addCleanup(os.unlink, path)

        with patch.object(config, "UPPER_IMAGE_PATH", path):
            content = claude.build_content("how are the plants?")

        self.assertEqual(content[0]["type"], "image", "image must come first")
        self.assertEqual(content[0]["source"]["media_type"], "image/jpeg")
        self.assertEqual(content[1]["type"], "text")
        self.assertIn("how are the plants?", content[1]["text"])

    def test_missing_image_is_omitted_not_fatal(self):
        with patch.object(config, "UPPER_IMAGE_PATH", "/nonexistent/x.jpg"):
            content = claude.build_content("hello")
        self.assertEqual([b["type"] for b in content], ["text"])

    def test_include_image_false_skips_frame(self):
        with patch.object(claude, "_image_block") as mock_img:
            content = claude.build_content("hello", include_image=False)
        mock_img.assert_not_called()
        self.assertEqual([b["type"] for b in content], ["text"])

    def test_embedded_state_is_valid_json(self):
        content = claude.build_content("q", include_image=False)
        text = content[0]["text"]
        json.loads(text[text.index("{") : text.rindex("}") + 1])


class AdviseTestCase(unittest.TestCase):
    @patch.object(config, "ANTHROPIC_API_KEY", "")
    def test_unconfigured_raises(self):
        with self.assertRaises(claude.AdviceError):
            claude.advise("anything")

    @patch.object(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    @patch.object(config, "ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    @patch.object(claude, "build_content", return_value=[{"type": "text", "text": "ctx"}])
    @patch.object(claude, "_client")
    def test_returns_text_and_usage(self, mock_client, _content):
        mock_client.return_value.messages.create.return_value = _response("Raise the light.")
        result = claude.advise("what now?")
        self.assertEqual(result["advice"], "Raise the light.")
        self.assertEqual(result["model"], "claude-haiku-4-5-20251001")
        self.assertEqual(result["usage"], {"input_tokens": 1234, "output_tokens": 56})

    @patch.object(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    @patch.object(claude, "_client")
    def test_api_error_does_not_leak_the_key(self, mock_client):
        secret = "sk-ant-supersecret"
        mock_client.return_value.messages.create.side_effect = RuntimeError(
            f"connection failed with header x-api-key: {secret}"
        )
        with self.assertRaises(claude.AdviceError) as ctx:
            claude.advise("q")
        # The generic message must not echo the SDK exception text.
        self.assertNotIn(secret, str(ctx.exception))
        self.assertIn("RuntimeError", str(ctx.exception))

    def test_missing_sdk_reports_advice_error(self):
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *a, **k):
            if name == "anthropic":
                raise ImportError("No module named 'anthropic'")
            return real_import(name, *a, **k)

        with patch.object(builtins, "__import__", fake_import):
            with self.assertRaises(claude.AdviceError) as ctx:
                claude._client()
        self.assertIn("not installed", str(ctx.exception))


class AdviceRouteTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app("default")
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch.object(config, "ANTHROPIC_API_KEY", "")
    def test_missing_question_is_400(self):
        self.assertEqual(self.client.post("/advice", json={}).status_code, 400)
        self.assertEqual(self.client.post("/advice", json={"question": "   "}).status_code, 400)

    @patch.object(config, "ANTHROPIC_API_KEY", "")
    def test_unconfigured_is_503(self):
        r = self.client.post("/advice", json={"question": "how are they?"})
        self.assertEqual(r.status_code, 503)

    @patch.object(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    @patch.object(claude, "advise")
    def test_success(self, mock_advise):
        mock_advise.return_value = {
            "advice": "Add water.",
            "model": "claude-haiku-4-5-20251001",
            "usage": {"input_tokens": 1, "output_tokens": 2},
        }
        r = self.client.post("/advice", json={"question": "water?"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["advice"], "Add water.")

    @patch.object(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    @patch.object(claude, "advise")
    def test_upstream_failure_is_502(self, mock_advise):
        mock_advise.side_effect = claude.AdviceError("Claude request failed (APIStatusError)")
        r = self.client.post("/advice", json={"question": "water?"})
        self.assertEqual(r.status_code, 502)

    @patch.object(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    @patch.object(claude, "advise")
    def test_include_image_is_forwarded(self, mock_advise):
        mock_advise.return_value = {"advice": "ok", "model": "m", "usage": {}}
        self.client.post("/advice", json={"question": "q", "include_image": False})
        self.assertFalse(mock_advise.call_args.kwargs["include_image"])


class AdviceKeyHeaderTestCase(unittest.TestCase):
    """X-Claude-Key carries the browser-held key through to the integration."""

    def setUp(self):
        app = create_app("default")
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch.object(config, "ANTHROPIC_API_KEY", "")
    @patch.object(claude, "advise")
    def test_header_key_is_passed_through(self, mock_advise):
        mock_advise.return_value = {"advice": "ok", "model": "m", "usage": {}}
        r = self.client.post(
            "/advice",
            json={"question": "q"},
            headers={"X-Claude-Key": "sk-ant-from-browser"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(mock_advise.call_args.kwargs["api_key"], "sk-ant-from-browser")

    @patch.object(config, "ANTHROPIC_API_KEY", "")
    def test_no_key_anywhere_is_503(self):
        r = self.client.post("/advice", json={"question": "q"})
        self.assertEqual(r.status_code, 503)
        self.assertIn("no Claude API key", r.get_json()["error"])

    @patch.object(config, "ANTHROPIC_API_KEY", "")
    @patch.object(config, "GARDEN_ADMIN_PASSWORD", "s3cret")
    def test_advice_is_covered_by_admin_auth(self):
        # The advice endpoint must not be a way around the admin password.
        r_env = {"REMOTE_ADDR": "203.0.113.9"}
        app = create_app("default")
        app.config["TESTING"] = True
        c = app.test_client()
        # No admin password -> 401 before the Claude key is even considered.
        self.assertEqual(
            c.post("/advice", json={"question": "q"}, environ_base=r_env).status_code, 401
        )
        # With the admin password, it proceeds past auth (and then 503s for the
        # missing Claude key, which is a different gate).
        r = c.post(
            "/advice",
            json={"question": "q"},
            headers={"X-API-Key": "s3cret", "X-Claude-Key": "sk-ant-x"},
            environ_base=r_env,
        )
        self.assertNotEqual(r.status_code, 401)


if __name__ == "__main__":
    unittest.main()
