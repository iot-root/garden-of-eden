import json
import os
import tempfile
import unittest

from app.lib.persist import write_json_atomic


class WriteJsonAtomicTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "data.json")

    def test_writes_and_overwrites(self):
        write_json_atomic(self.path, {"a": 1})
        self.assertEqual(json.load(open(self.path)), {"a": 1})
        write_json_atomic(self.path, {"a": 2, "b": [1, 2]})
        self.assertEqual(json.load(open(self.path)), {"a": 2, "b": [1, 2]})

    def test_leaves_no_temp_files(self):
        write_json_atomic(self.path, {"x": 1})
        leftovers = [f for f in os.listdir(self.dir) if f.endswith(".tmp")]
        self.assertEqual(leftovers, [])

    def test_failed_write_keeps_old_file(self):
        write_json_atomic(self.path, {"good": True})
        # A non-serializable payload raises and must NOT clobber the existing file.
        with self.assertRaises(TypeError):
            write_json_atomic(self.path, {"bad": {1, 2, 3}})
        self.assertEqual(json.load(open(self.path)), {"good": True})
        self.assertEqual([f for f in os.listdir(self.dir) if f.endswith(".tmp")], [])


if __name__ == "__main__":
    unittest.main()
