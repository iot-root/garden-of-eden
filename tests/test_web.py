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

    def test_advice_card_is_present(self):
        # The web UI is the only way most operators will reach /advice, so the
        # card and its wiring must ship with the page.
        html = self.client.get("/").data.decode()
        for needle in (
            'id="advice"',
            'id="advice-q"',
            'id="advice-send"',
            'id="advice-out"',
            'id="advice-usage"',
            'id="advice-presets"',
            "function askGroq(",
            "setupAdvice();",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, html)

    def test_advice_card_posts_to_the_endpoint(self):
        html = self.client.get("/").data.decode()
        # The presets must send a non-empty question, and the call must go to
        # /advice with the admin password attached when one is stored.
        self.assertIn('data-q="', html)
        self.assertIn('"/advice"', html)
        self.assertIn("headers(", html)

    def test_groq_key_is_settable_in_settings(self):
        html = self.client.get("/").data.decode()
        for needle in (
            'id="groq-key"',
            "function saveGroqKey()",
            'localStorage.setItem("groq_key"',
            "adviceHeaders(",
            'localStorage.getItem("groq_key")',
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, html)

    def test_advice_is_gated_on_the_admin_password(self):
        html = self.client.get("/").data.decode()
        # Only the admin password gates the control: the endpoint 401s without
        # it and no server-side setting can replace it. The Groq key must NOT
        # gate it, because the Pi can hold GROQ_API_KEY in its own .env and the
        # endpoint falls back to that -- gating on the key would grey out a
        # control that works. A missing key everywhere surfaces as a 503 whose
        # message the send path shows.
        self.assertIn("function syncAdviceGate()", html)
        self.assertIn("if (!API_KEY || !GROQ_KEY)", html)
        self.assertIn("your admin password", html)
        self.assertIn('id="advice-gate"', html)
        # The gate itself must only ever ask for the admin password.
        gate = html[html.index("function missingAdviceCreds(") :]
        gate = gate[: gate.index("function syncAdviceGate(")]
        self.assertIn("API_KEY ? []", gate)
        self.assertNotIn("GROQ_KEY", gate)

    def test_groq_key_only_attached_to_advice(self):
        html = self.client.get("/").data.decode()
        # The third-party credential must not ride along on every request.
        self.assertIn('GROQ_KEY ? { "X-Groq-Key": GROQ_KEY } : {}', html)
        # ...and the ask call must use adviceHeaders, not bare headers.
        ask = html[html.index("async function askGroq(") :]
        self.assertIn("adviceHeaders(", ask)

    def test_disabled_advice_controls_look_disabled(self):
        html = self.client.get("/").data.decode()
        # A disabled button swallows clicks with zero feedback, so every disabled
        # control has to be visibly disabled. This rule used to target only
        # button.btn, which left the Ask Groq presets full-colour with a
        # pointer cursor while being unclickable: a dead control that looked
        # alive, so clicking a preset did nothing at all.
        self.assertIn("button[disabled]", html)
        self.assertNotIn("button.btn[disabled]", html)
        # The preset hover effect must not survive the disabled state.
        self.assertIn(".presets button[disabled]:hover", html)

    def test_advice_send_never_fails_silently(self):
        html = self.client.get("/").data.decode()
        # If the gate is stale -- a key cleared in another tab after the page
        # loaded -- the send path must name what is missing instead of returning
        # without a word.
        ask = html[html.index("async function askGroq(") :]
        self.assertIn("missingAdviceCreds()", ask)
        self.assertIn("in Settings first.", ask)
        # The gate hint is an instruction, not faint fine print.
        self.assertIn("#advice-gate:not(:empty)", html)


if __name__ == "__main__":
    unittest.main()
