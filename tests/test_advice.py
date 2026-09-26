"""Groq advice integration (issue #101).

The Groq SDK is never installed in the test environment and is never called:
``_client`` is patched. These tests cover snapshot assembly, the disabled path,
the image part, the chat-completions request shape, and the route's status codes.
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
from app.integrations import groq

DEFAULT_MODEL = "qwen/qwen3.8-27b"


@contextlib.contextmanager
def _fake_groq():
    """Inject a stub ``groq`` module.

    The SDK is not a test dependency (requirements-dev.txt is pure-Python and
    the integration imports it lazily), so tests that reach ``_client()``
    supply a stand-in and assert on how it was constructed.
    """
    mod = types.ModuleType("groq")
    mock_cls = MagicMock(name="Groq")
    mod.Groq = mock_cls
    with patch.dict(sys.modules, {"groq": mod}):
        yield mock_cls


def _response(text="Looks healthy.", in_tokens=1234, out_tokens=56, reasoning=None):
    """A stand-in for a groq chat completion."""
    message = MagicMock()
    message.content = text
    message.reasoning = reasoning
    usage = MagicMock()
    usage.prompt_tokens = in_tokens
    usage.completion_tokens = out_tokens
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]
    completion.usage = usage
    return completion


class IsEnabledTestCase(unittest.TestCase):
    @patch.object(config, "GROQ_API_KEY", "")
    def test_disabled_without_key(self):
        self.assertFalse(groq.is_enabled())

    @patch.object(config, "GROQ_API_KEY", "gsk_test")
    def test_enabled_with_key(self):
        self.assertTrue(groq.is_enabled())


class PerRequestKeyTestCase(unittest.TestCase):
    """The browser supplies the Groq key per request (X-Groq-Key)."""

    @patch.object(config, "GROQ_API_KEY", "")
    def test_request_key_enables_with_no_server_key(self):
        self.assertFalse(groq.is_enabled())
        self.assertTrue(groq.is_enabled("gsk_from_browser"))

    @patch.object(config, "GROQ_API_KEY", "gsk_server")
    def test_server_key_still_works(self):
        self.assertTrue(groq.is_enabled())
        self.assertTrue(groq.is_enabled("gsk_from_browser"))

    @patch.object(config, "GROQ_API_KEY", "gsk_server")
    def test_whitespace_only_request_key_falls_back(self):
        # A blank header must not count as a supplied key.
        self.assertTrue(groq.is_enabled("   "))

    @patch.object(config, "GROQ_API_KEY", "")
    def test_client_prefers_the_request_key(self):
        with _fake_groq() as mock_cls:
            groq._client("gsk_from_browser")
        self.assertEqual(mock_cls.call_args.kwargs["api_key"], "gsk_from_browser")

    @patch.object(config, "GROQ_API_KEY", "gsk_server")
    def test_client_falls_back_to_server_key(self):
        with _fake_groq() as mock_cls:
            groq._client("")
        self.assertEqual(mock_cls.call_args.kwargs["api_key"], "gsk_server")


class SnapshotTestCase(unittest.TestCase):
    def test_snapshot_has_expected_keys(self):
        state = groq.snapshot()
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
        with patch.object(groq, "_read", side_effect=lambda label, fn: None):
            state = groq.snapshot()
        self.assertIsNone(state["air_temperature_c"])
        self.assertIsNone(state["humidity_percent"])
        self.assertIsNone(state["pcb_temperature_c"])

    def test_days_since_handles_garbage(self):
        self.assertIsNone(groq._days_since("not-a-date"))
        self.assertIsNone(groq._days_since(None))


class BuildContentTestCase(unittest.TestCase):
    def test_image_part_precedes_text(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as fh:
            fh.write(b"\xff\xd8\xff\xd9fake-jpeg")
            path = fh.name
        self.addCleanup(os.unlink, path)

        with patch.object(config, "UPPER_IMAGE_PATH", path):
            content = groq.build_content("how are the plants?")

        # Groq is OpenAI-compatible: images are image_url parts carrying a
        # base64 data URI, not Anthropic-style base64 source blocks.
        self.assertEqual(content[0]["type"], "image_url", "image must come first")
        self.assertTrue(content[0]["image_url"]["url"].startswith("data:image/jpeg;base64,"))
        self.assertEqual(content[1]["type"], "text")
        self.assertIn("how are the plants?", content[1]["text"])

    def test_missing_image_is_omitted_not_fatal(self):
        with patch.object(config, "UPPER_IMAGE_PATH", "/nonexistent/x.jpg"):
            content = groq.build_content("hello")
        self.assertEqual([b["type"] for b in content], ["text"])

    def test_include_image_false_skips_frame(self):
        with patch.object(groq, "_image_block") as mock_img:
            content = groq.build_content("hello", include_image=False)
        mock_img.assert_not_called()
        self.assertEqual([b["type"] for b in content], ["text"])


class AdviseTestCase(unittest.TestCase):
    @patch.object(config, "GROQ_API_KEY", "")
    def test_unconfigured_raises(self):
        with self.assertRaises(groq.AdviceError):
            groq.advise("anything")

    @patch.object(config, "GROQ_API_KEY", "gsk_test")
    @patch.object(config, "GROQ_MODEL", DEFAULT_MODEL)
    @patch.object(groq, "build_content", return_value=[{"type": "text", "text": "ctx"}])
    @patch.object(groq, "_client")
    def test_returns_text_and_usage(self, mock_client, _content):
        mock_client.return_value.chat.completions.create.return_value = _response(
            "Raise the light."
        )
        result = groq.advise("what now?")
        self.assertEqual(result["advice"], "Raise the light.")
        self.assertEqual(result["model"], DEFAULT_MODEL)
        self.assertEqual(result["usage"], {"input_tokens": 1234, "output_tokens": 56})

    @patch.object(config, "GROQ_API_KEY", "gsk_test")
    @patch.object(groq, "build_content", return_value=[{"type": "text", "text": "ctx"}])
    @patch.object(groq, "_client")
    def test_request_uses_chat_completions_shape(self, mock_client, _content):
        mock_client.return_value.chat.completions.create.return_value = _response()
        groq.advise("what now?")
        kwargs = mock_client.return_value.chat.completions.create.call_args.kwargs
        self.assertEqual(kwargs["model"], DEFAULT_MODEL)
        # Groq takes the system prompt as a message, not a system= argument.
        self.assertNotIn("system", kwargs)
        roles = [m["role"] for m in kwargs["messages"]]
        self.assertEqual(roles, ["system", "user"])

    @patch.object(config, "GROQ_API_KEY", "gsk_test")
    @patch.object(groq, "_client")
    def test_api_error_does_not_leak_the_key(self, mock_client):
        secret = "gsk_supersecret"
        mock_client.return_value.chat.completions.create.side_effect = RuntimeError(
            f"connection failed with header Authorization: Bearer {secret}"
        )
        with self.assertRaises(groq.AdviceError) as ctx:
            groq.advise("q")
        # The message must not echo the SDK exception text.
        self.assertNotIn(secret, str(ctx.exception))
        self.assertIn("RuntimeError", str(ctx.exception))

    @patch.object(config, "GROQ_API_KEY", "gsk_test")
    @patch.object(groq, "_client")
    def test_empty_response_is_reported(self, mock_client):
        mock_client.return_value.chat.completions.create.return_value = _response(text="")
        with self.assertRaises(groq.AdviceError) as ctx:
            groq.advise("q")
        self.assertIn("empty response", str(ctx.exception))

    @patch.object(config, "GROQ_API_KEY", "gsk_test")
    @patch.object(groq, "_client")
    def test_reasoning_fallback_is_used(self, mock_client):
        # qwen3.8-27b can answer in a reasoning mode where content is empty and
        # the text arrives in `reasoning`; an empty response would be wrong.
        mock_client.return_value.chat.completions.create.return_value = _response(
            text="", reasoning="The leaves look pale."
        )
        self.assertEqual(groq.advise("q")["advice"], "The leaves look pale.")

    def test_missing_sdk_reports_advice_error(self):
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *a, **k):
            if name == "groq":
                raise ImportError("No module named 'groq'")
            return real_import(name, *a, **k)

        with patch.object(builtins, "__import__", fake_import):
            with self.assertRaises(groq.AdviceError) as ctx:
                groq._client()
        self.assertIn("not installed", str(ctx.exception))


class ErrorDetailTestCase(unittest.TestCase):
    """A bare "BadRequestError" cannot be acted on.

    ``_error_detail`` pulls the API's own error type/message out of the
    response body, which is what actually explains a failure (unknown model id,
    oversized image, rate limit, revoked key).
    """

    def _exc(self, **attrs):
        exc = RuntimeError("boom")
        for name, value in attrs.items():
            setattr(exc, name, value)
        return exc

    def test_uses_api_error_type_and_message(self):
        exc = self._exc(
            body={"error": {"type": "invalid_request_error", "message": "model not found"}},
            status_code=400,
        )
        self.assertEqual(groq._error_detail(exc), "invalid_request_error: model not found")

    def test_handles_message_only_and_type_only(self):
        self.assertEqual(
            groq._error_detail(self._exc(body={"error": {"message": "bad model"}})),
            "bad model",
        )
        self.assertEqual(
            groq._error_detail(self._exc(body={"error": {"type": "rate_limit_error"}})),
            "rate_limit_error",
        )

    def test_falls_back_to_status_then_class_name(self):
        self.assertEqual(groq._error_detail(self._exc(status_code=429)), "HTTP 429")
        self.assertEqual(groq._error_detail(RuntimeError("boom")), "RuntimeError")
        self.assertEqual(groq._error_detail(self._exc(body="not a dict")), "RuntimeError")

    @patch.object(config, "GROQ_API_KEY", "gsk_test")
    @patch.object(groq, "_client")
    def test_advise_surfaces_the_detail(self, mock_client):
        mock_client.return_value.chat.completions.create.side_effect = self._exc(
            body={"error": {"type": "invalid_request_error", "message": "model not found"}},
            status_code=400,
        )
        with self.assertRaises(groq.AdviceError) as ctx:
            groq.advise("q")
        self.assertIn("model not found", str(ctx.exception))

    def test_embedded_state_is_valid_json(self):
        content = groq.build_content("q", include_image=False)
        text = content[0]["text"]
        json.loads(text[text.index("{") : text.rindex("}") + 1])


class AdviceRouteTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app("default")
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch.object(config, "GROQ_API_KEY", "")
    def test_missing_question_is_400(self):
        self.assertEqual(self.client.post("/advice", json={}).status_code, 400)
        self.assertEqual(self.client.post("/advice", json={"question": "   "}).status_code, 400)

    @patch.object(config, "GROQ_API_KEY", "")
    def test_unconfigured_is_503(self):
        r = self.client.post("/advice", json={"question": "how are they?"})
        self.assertEqual(r.status_code, 503)
        self.assertIn("no Groq API key", r.get_json()["error"])

    @patch.object(config, "GROQ_API_KEY", "gsk_test")
    @patch.object(groq, "advise")
    def test_success(self, mock_advise):
        mock_advise.return_value = {
            "advice": "Add water.",
            "model": DEFAULT_MODEL,
            "usage": {"input_tokens": 1, "output_tokens": 2},
        }
        r = self.client.post("/advice", json={"question": "water?"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["advice"], "Add water.")

    @patch.object(config, "GROQ_API_KEY", "gsk_test")
    @patch.object(groq, "advise")
    def test_upstream_failure_is_502(self, mock_advise):
        mock_advise.side_effect = groq.AdviceError("Groq request failed (APIStatusError)")
        r = self.client.post("/advice", json={"question": "water?"})
        self.assertEqual(r.status_code, 502)

    @patch.object(config, "GROQ_API_KEY", "gsk_test")
    @patch.object(groq, "advise")
    def test_include_image_is_forwarded(self, mock_advise):
        mock_advise.return_value = {"advice": "ok", "model": "m", "usage": {}}
        self.client.post("/advice", json={"question": "q", "include_image": False})
        self.assertFalse(mock_advise.call_args.kwargs["include_image"])


class AdviceKeyHeaderTestCase(unittest.TestCase):
    """X-Groq-Key carries the browser-held key through to the integration."""

    def setUp(self):
        app = create_app("default")
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch.object(config, "GROQ_API_KEY", "")
    @patch.object(groq, "advise")
    def test_header_key_is_passed_through(self, mock_advise):
        mock_advise.return_value = {"advice": "ok", "model": "m", "usage": {}}
        r = self.client.post(
            "/advice",
            json={"question": "q"},
            headers={"X-Groq-Key": "gsk_from_browser"},
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(mock_advise.call_args.kwargs["api_key"], "gsk_from_browser")

    @patch.object(config, "GROQ_API_KEY", "")
    def test_no_key_anywhere_is_503(self):
        r = self.client.post("/advice", json={"question": "q"})
        self.assertEqual(r.status_code, 503)
        self.assertIn("no Groq API key", r.get_json()["error"])

    @patch.object(config, "GROQ_API_KEY", "")
    @patch.object(config, "GARDEN_ADMIN_PASSWORD", "s3cret")
    def test_advice_is_covered_by_admin_auth(self):
        # The advice endpoint must not be a way around the admin password.
        r_env = {"REMOTE_ADDR": "203.0.113.9"}
        app = create_app("default")
        app.config["TESTING"] = True
        c = app.test_client()
        # No admin password -> 401 before the Groq key is even considered.
        self.assertEqual(
            c.post("/advice", json={"question": "q"}, environ_base=r_env).status_code, 401
        )
        # With the admin password, it proceeds past auth (and then 503s for the
        # missing Groq key, which is a different gate).
        r = c.post(
            "/advice",
            json={"question": "q"},
            headers={"X-API-Key": "s3cret", "X-Groq-Key": "gsk_x"},
            environ_base=r_env,
        )
        self.assertNotEqual(r.status_code, 401)


if __name__ == "__main__":
    unittest.main()
