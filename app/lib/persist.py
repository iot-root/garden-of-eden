"""Atomic JSON persistence shared by the state/schedule/pods/grow stores.

Writing to a temp file and ``os.replace``-ing it means a power cut mid-write
can't leave a half-written (corrupt) file on the SD card -- the old file stays
intact until the new one is complete.
"""

import json
import os
import tempfile


def write_json_atomic(path, data):
    """Atomically write ``data`` as JSON to ``path`` (temp file + fsync + replace)."""
    directory = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=2)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
