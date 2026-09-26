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
            "function askClaude(",
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

    def test_claude_key_is_settable_in_settings(self):
        html = self.client.get("/").data.decode()
        for needle in (
            'id="claude-key"',
            "function saveClaudeKey()",
            'localStorage.setItem("claude_key"',
            "adviceHeaders(",
            'localStorage.getItem("claude_key")',
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, html)

    def test_advice_is_gated_on_both_credentials(self):
        html = self.client.get("/").data.decode()
        # Ask Claude must be refused unless BOTH the admin password and a
        # Claude key are present in the browser.
        self.assertIn("function syncAdviceGate()", html)
        self.assertIn("if (!API_KEY || !CLAUDE_KEY)", html)
        self.assertIn('need.push("your admin password")', html)
        self.assertIn('need.push("a Claude API key")', html)
        self.assertIn('id="advice-gate"', html)

    def test_claude_key_only_attached_to_advice(self):
        html = self.client.get("/").data.decode()
        # The third-party credential must not ride along on every request.
        self.assertIn('CLAUDE_KEY ? { "X-Claude-Key": CLAUDE_KEY } : {}', html)
        # ...and the ask call must use adviceHeaders, not bare headers.
        ask = html[html.index("async function askClaude(") :]
        self.assertIn("adviceHeaders(", ask)


if __name__ == "__main__":
    unittest.main()
