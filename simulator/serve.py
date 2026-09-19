"""Run the web UI + REST API locally with simulated hardware.

    python -m simulator.serve            # http://localhost:5000/

No Raspberry Pi, pigpiod, or sensors required. Camera endpoints return a
placeholder image so the UI renders end to end.
"""

import base64
import os

# Seed sim-friendly config BEFORE importing config/app (config reads env at import).
os.environ.setdefault("SENSOR_TYPE", "DHT20")
os.environ.setdefault("GARDYN_MODEL", "gardyn 3.0 (simulated)")
os.environ.setdefault("WATER_LOW_CM", "11")
os.environ.setdefault("LOG_LEVEL", "INFO")
# Keep simulated state files out of the real home dir.
_state = os.path.join(os.path.dirname(__file__), ".sim")
os.makedirs(_state, exist_ok=True)
os.environ.setdefault("STATE_FILE", os.path.join(_state, "state.json"))
os.environ.setdefault("GROW_STATE_FILE", os.path.join(_state, "grow.json"))
os.environ.setdefault("SCHEDULE_FILE", os.path.join(_state, "schedule.json"))

from simulator import fake_hardware  # noqa: E402

fake_hardware.install()

from app import create_app  # noqa: E402
from app.lib.logging_config import configure_logging  # noqa: E402
from app.sensors.camera import camera as _camera  # noqa: E402
from app.sensors.schedule import schedule as _schedule  # noqa: E402

# Never touch the host's real crontab in simulation — schedules are still saved
# to the sandboxed SCHEDULE_FILE so the UI round-trips, but no cron is written.
_schedule._read_crontab = lambda: []
_schedule._write_crontab = lambda lines: None

# 1x1 JPEG used as a stand-in for real camera frames.
_PLACEHOLDER_JPEG = base64.b64decode(
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRof"
    "Hh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/wAALCAABAAEBAREA/8QAFAAB"
    "AAAAAAAAAAAAAAAAAAAACP/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AfwD/2Q=="
)


def _fake_capture(device, output_path, resolution=None):
    with open(output_path, "wb") as fh:
        fh.write(_PLACEHOLDER_JPEG)
    return output_path


# Route camera capture to the placeholder (no fswebcam needed).
_camera.capture = _fake_capture

configure_logging()
app = create_app()

if __name__ == "__main__":
    print("Garden of Eden simulator (web + REST) on http://localhost:5000/")
    # Reloader off: single clean process, no double-init of simulated state.
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
