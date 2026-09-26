import os
import tempfile
import unittest
from unittest import mock

import config
from app.lib import hardware
from app.lib import pods as pods_lib


class PodsTestCase(unittest.TestCase):
    def test_default_count(self):
        # The pod list length follows the resolved capacity, which is the model
        # profile unless .env overrides it.
        self.assertEqual(len(pods_lib.default_pods()), hardware.pod_capacity())

    def test_normalize_cleans_and_fills(self):
        raw = [
            {
                "id": 1,
                "name": "Basil",
                "symbols": ["circle", "bogus", "square", "star", "heart", "plus", "circle"],
            }
        ]
        pods = pods_lib.normalize(raw)
        self.assertEqual(len(pods), hardware.pod_capacity())
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


class PodPositionTestCase(unittest.TestCase):
    """Physical position is derived from the layout config, never stored."""

    def _pos(self, pod_id, columns, pattern):
        with (
            mock.patch.object(config, "POD_COUNT", 16),
            mock.patch.object(config, "POD_COLUMNS", columns),
            mock.patch.object(config, "POD_SIDE_PATTERN", pattern),
        ):
            return pods_lib.position_for(pod_id)

    def test_two_columns_fill_down_then_across(self):
        self.assertEqual(self._pos(1, 2, "")["column"], 1)
        self.assertEqual(self._pos(8, 2, "")["column"], 1)
        self.assertEqual(self._pos(9, 2, "")["column"], 2)
        self.assertEqual(self._pos(16, 2, "")["column"], 2)

    def test_level_is_one_based_from_the_top(self):
        # Level is the axis that matters: the grow light is at the top.
        self.assertEqual(self._pos(1, 2, "")["level"], 1)
        self.assertEqual(self._pos(8, 2, "")["level"], 8)
        # Second column restarts at the top of the tower.
        self.assertEqual(self._pos(9, 2, "")["level"], 1)
        self.assertEqual(self._pos(16, 2, "")["level"], 8)

    def test_side_alternates_from_the_highest_pod(self):
        # "rlrlrlrl" means the top pod sticks out right, then left, and so on.
        sides = [self._pos(i, 2, "rlrlrlrl")["side"] for i in range(1, 9)]
        self.assertEqual(sides, ["r", "l", "r", "l", "r", "l", "r", "l"])

    def test_both_columns_share_the_side_pattern(self):
        # Pod 1 and pod 9 are the same height in different columns, so the side
        # they stick out on must match even though the column differs.
        for level in range(1, 9):
            left = self._pos(level, 2, "rlrlrlrl")
            right = self._pos(level + 8, 2, "rlrlrlrl")
            self.assertEqual(left["level"], right["level"])
            self.assertEqual(left["side"], right["side"])

    def test_no_pattern_means_no_side(self):
        self.assertIsNone(self._pos(1, 2, "")["side"])

    def test_short_pattern_leaves_remaining_levels_unset(self):
        self.assertEqual(self._pos(1, 2, "r")["side"], "r")
        self.assertIsNone(self._pos(2, 2, "r")["side"])

    def test_single_column_is_the_flat_default(self):
        # A unit with no configured geometry still gets sane positions.
        pos = self._pos(5, 1, "")
        self.assertEqual(pos, {"column": 1, "level": 5, "side": None})

    def test_uneven_last_column_does_not_crash(self):
        with (
            mock.patch.object(config, "POD_COUNT", 10),
            mock.patch.object(config, "POD_COLUMNS", 4),
            mock.patch.object(config, "POD_SIDE_PATTERN", ""),
        ):
            pos = pods_lib.position_for(10)
        self.assertEqual(pos["column"], 4)
        self.assertEqual(pos["level"], 1)

    def test_bad_column_count_falls_back_to_one(self):
        pos = self._pos(3, 0, "")
        self.assertEqual(pos["column"], 1)
        self.assertEqual(pos["level"], 3)

    def test_position_is_not_persisted(self):
        # Derived data must not reach the state file, or it can go stale.
        with (
            mock.patch.object(config, "POD_COLUMNS", 2),
            mock.patch.object(config, "POD_SIDE_PATTERN", "rl"),
        ):
            self.assertNotIn("position", pods_lib.normalize([])[0])
            self.assertIn("position", pods_lib.with_positions(pods_lib.normalize([]))[0])

    def test_with_positions_does_not_mutate_input(self):
        raw = pods_lib.normalize([])
        pods_lib.with_positions(raw)
        self.assertNotIn("position", raw[0])


if __name__ == "__main__":
    unittest.main()
