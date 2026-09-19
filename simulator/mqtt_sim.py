"""Run the MQTT service with simulated hardware against a local broker, so Home
Assistant can discover and control the simulated Gardyn.

    # 1. start a broker (either of these):
    docker compose up broker          # bundled mosquitto on :1883
    #   or: sudo apt install mosquitto && sudo systemctl start mosquitto
    # 2. run the simulator:
    python -m simulator.mqtt_sim

Point Home Assistant's MQTT integration at the same broker; the simulated device
auto-discovers with all entities (light, pump, sensors, water alert, cameras,
button event). Override the broker with MQTT_BROKER / MQTT_PORT env vars.
"""

import os
import runpy

# Seed sim-friendly config before mqtt.py imports config.
os.environ.setdefault("SENSOR_TYPE", "DHT20")
os.environ.setdefault("GARDYN_MODEL", "gardyn 3.0 (simulated)")
os.environ.setdefault("WATER_LOW_CM", "11")
os.environ.setdefault("MQTT_BROKER", "localhost")
os.environ.setdefault("MQTT_PORT", "1883")
os.environ.setdefault("MQTT_IDENTIFIER", "gardyn_sim")
_state = os.path.join(os.path.dirname(__file__), ".sim")
os.makedirs(_state, exist_ok=True)
os.environ.setdefault("STATE_FILE", os.path.join(_state, "state.json"))
os.environ.setdefault("GROW_STATE_FILE", os.path.join(_state, "grow.json"))
os.environ.setdefault("SCHEDULE_FILE", os.path.join(_state, "schedule.json"))

from simulator import fake_hardware  # noqa: E402

fake_hardware.install()

# Sandbox the crontab writer so schedule changes from HA never touch the host's
# real crontab (mqtt.py's schedule toggles call apply_schedule). Mirrors the
# guard serve.py applies to the Flask /schedule route.
from app.sensors.schedule import schedule as _schedule  # noqa: E402

_schedule._read_crontab = lambda: []
_schedule._write_crontab = lambda lines: None

if __name__ == "__main__":
    print("Garden of Eden MQTT simulator -> broker", os.environ["MQTT_BROKER"])
    # Execute mqtt.py as __main__ with the fakes already in sys.modules.
    runpy.run_path(
        os.path.join(os.path.dirname(__file__), "..", "mqtt.py"),
        run_name="__main__",
    )
