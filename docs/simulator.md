# Simulator — test everything without a Pi

Run and manually test the full stack (web UI, REST API, and MQTT/Home Assistant
discovery) on a normal machine. Realistic fake hardware stands in for the
sensors and actuators, so the UI shows live, changing values.

## Setup

```bash
python -m venv .venv-dev
.venv-dev/bin/pip install -r requirements-dev.txt
```

## Web UI + REST API

```bash
.venv-dev/bin/python -m simulator.serve
# open http://localhost:5000/
```

- Sensors return believable values; the water level oscillates through the
  low-water threshold so you can watch the alert toggle.
- Light/pump remember their state, so brightness/speed sliders read back.
- Camera endpoints return a placeholder JPEG (no `fswebcam` needed).
- **Schedules are sandboxed**: saved to a local file under `simulator/.sim/` but
  the host crontab is never touched.

Hit the REST surface directly too:

```bash
curl localhost:5000/system
curl localhost:5000/temperature
curl -X POST -H 'Content-Type: application/json' -d '{"value":65}' localhost:5000/light/brightness
```

## MQTT + Home Assistant

```bash
# 1. start a broker
docker compose up broker          # bundled mosquitto on :1883
#    or: sudo apt install mosquitto && sudo systemctl start mosquitto

# 2. run the MQTT simulator
.venv-dev/bin/python -m simulator.mqtt_sim
```

Point Home Assistant's MQTT integration at the same broker. The simulated device
(`gardyn_sim`) auto-discovers with every entity: light, pump, temperature,
humidity, PCB temp, water level, water-low binary sensor + threshold number,
upper/lower camera images, and the button **event** entity (single/double/long).

Inspect discovery without HA using any MQTT client:

```bash
mosquitto_sub -t 'homeassistant/#' -v        # discovery configs
mosquitto_sub -t 'gardyn/#' -v               # live state/telemetry
mosquitto_pub -t 'gardyn/light/command' -m ON  # drive the simulated light
```

## Automated coverage

The same surfaces are covered by tests (no broker/Pi needed):

```bash
.venv-dev/bin/python -m unittest discover -t . -s tests -p 'test_*.py'
```

- `test_discovery.py` — asserts every HA discovery entity is announced with valid
  JSON payloads (validates the Home Assistant integration offline).
- `test_integration.py` — smoke-tests every GET route for unhandled 500s.
- Per-feature tests for camera, schedule, grow, config, water, state, etc.
