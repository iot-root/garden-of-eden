"""Recent-warning buffer in app/lib/logging_config.py.

The buffer exists so the advice integration can tell a model which parts of the
machine are misbehaving. It only ever holds WARNING+ records, it is bounded,
and it strips anything credential-shaped before a record can reach a
third-party model.
"""

import logging
import unittest

from app.lib import logging_config
from app.lib.logging_config import RecentWarningHandler, recent_warnings

LOGGER_NAME = "app.test_recent_warnings"


class _BufferCase(unittest.TestCase):
    def setUp(self):
        self._saved = list(logging_config._warnings)
        logging_config._warnings.clear()

        self.handler = RecentWarningHandler()
        # Log through a real logger so records travel the production path:
        # Logger.callHandlers is what applies the handler's level, not
        # Handler.handle. The logger is pinned to DEBUG so the handler's level
        # is the only thing doing the filtering -- otherwise .info() would be
        # dropped by the logger and the test would prove nothing.
        self.logger = logging.getLogger(LOGGER_NAME)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        logging_config._warnings.clear()
        logging_config._warnings.extend(self._saved)

    def emit(self, level, message):
        self.logger.log(level, message)


class CapturesOnlyWarningsTestCase(_BufferCase):
    def test_warning_and_error_are_captured(self):
        self.emit(logging.WARNING, "distance sensor no echo")
        self.emit(logging.ERROR, "pump did not start")
        entries = recent_warnings()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["level"], "WARNING")
        self.assertEqual(entries[1]["level"], "ERROR")
        self.assertEqual(entries[0]["message"], "distance sensor no echo")
        self.assertEqual(entries[0]["logger"], LOGGER_NAME)

    def test_info_and_debug_are_ignored(self):
        # Routine refresh chatter must not crowd out real faults. The logger
        # above is at DEBUG, so this can only pass if the handler filters.
        self.emit(logging.INFO, "routine refresh")
        self.emit(logging.DEBUG, "noisy internals")
        self.assertEqual(recent_warnings(), [])

    def test_handler_level_is_pinned_to_warning(self):
        # A NOTSET handler would capture INFO too; pin it explicitly.
        self.assertEqual(self.handler.level, logging.WARNING)

    def test_timestamp_is_stamped(self):
        self.emit(logging.WARNING, "something")
        self.assertRegex(recent_warnings()[0]["time"], r"^\d{2}:\d{2}:\d{2}$")


class RedactionTestCase(_BufferCase):
    def test_anthropic_key_is_stripped(self):
        self.emit(logging.WARNING, "auth failed for sk-ant-api03-AAAABBBBCCCCDDDD")
        self.assertNotIn("sk-ant", recent_warnings()[0]["message"])
        self.assertIn("[redacted]", recent_warnings()[0]["message"])

    def test_groq_key_is_stripped(self):
        # An obviously fake key: never paste a real one into a test.
        self.emit(logging.ERROR, "key gsk_ExampleFakeKey0000 was rejected")
        message = recent_warnings()[0]["message"]
        self.assertNotIn("gsk_ExampleFakeKey0000", message)
        self.assertIn("[redacted]", message)

    def test_bearer_token_is_stripped(self):
        self.emit(logging.WARNING, "Authorization: Bearer abcdef123456")
        self.assertNotIn("abcdef123456", recent_warnings()[0]["message"])

    def test_ordinary_text_survives(self):
        self.emit(logging.WARNING, "DistanceSensorNoEcho: no echo received")
        self.assertEqual(recent_warnings()[0]["message"], "DistanceSensorNoEcho: no echo received")


class BoundsTestCase(_BufferCase):
    def test_buffer_is_bounded(self):
        # A Pi has to be able to run this indefinitely.
        for i in range(logging_config._WARNINGS_MAX + 25):
            self.emit(logging.WARNING, f"event {i}")
        self.assertEqual(len(logging_config._warnings), logging_config._WARNINGS_MAX)

    def test_oldest_entries_are_dropped_first(self):
        for i in range(logging_config._WARNINGS_MAX + 5):
            self.emit(logging.WARNING, f"event {i}")
        newest = recent_warnings(limit=1)[0]["message"]
        self.assertEqual(newest, f"event {logging_config._WARNINGS_MAX + 4}")

    def test_limit_returns_the_tail_oldest_first(self):
        for i in range(5):
            self.emit(logging.WARNING, f"event {i}")
        entries = recent_warnings(limit=2)
        self.assertEqual([e["message"] for e in entries], ["event 3", "event 4"])

    def test_non_positive_limit_returns_nothing(self):
        self.emit(logging.WARNING, "something")
        self.assertEqual(recent_warnings(limit=0), [])
        self.assertEqual(recent_warnings(limit=-1), [])

    def test_long_messages_are_truncated(self):
        self.emit(logging.WARNING, "x" * 5000)
        self.assertLessEqual(len(recent_warnings()[0]["message"]), 300)

    def test_returned_entries_are_copies(self):
        # A caller mutating the result must not corrupt the buffer.
        self.emit(logging.WARNING, "original")
        entry = recent_warnings()[0]
        entry["message"] = "tampered"
        self.assertEqual(recent_warnings()[0]["message"], "original")

    def test_empty_when_nothing_logged(self):
        self.assertEqual(recent_warnings(), [])


if __name__ == "__main__":
    unittest.main()
