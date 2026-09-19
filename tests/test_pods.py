import os
import tempfile
import unittest
from unittest import mock

import config
from app.lib import pods as pods_lib


class PodsTestCase(unittest.TestCase):
    def test_default_count(self):
        self.assertEqual(len(pods_lib.default_pods()), config.POD_COUNT)

    def test_normalize_cleans_and_fills(self):
        raw = [
            {
                "id": 1,
                "name": "Basil",
                "symbols": ["circle", "bogus", "square", "star", "heart", "plus", "circle"],
            }
        ]
        pods = pods_lib.normalize(raw)
        self.assertEqual(len(pods), config.POD_COUNT)
        self.assertEqual(pods[0]["name"], "Basil")
        # 'bogus' dropped; capped at 5 symbols.
        self.assertEqual(pods[0]["symbols"], ["circle", "square", "star", "heart", "plus"])
        self.assertEqual(pods[1]["symbols"], [])

    def test_save_set_roundtrip(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            path = fh.name
        try:
            with mock.patch.object(config, "PODS_FILE", path):
                pods_lib.save_pods([{"id": 2, "name": "Mint", "symbols": ["star"]}])
                loaded = pods_lib.load_pods()
                self.assertEqual(loaded[1]["name"], "Mint")
                self.assertEqual(loaded[1]["symbols"], ["star"])
                pods_lib.set_pod(2, name="Spearmint")
                self.assertEqual(pods_lib.load_pods()[1]["name"], "Spearmint")
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
