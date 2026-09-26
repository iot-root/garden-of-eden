# Project Context

## Purpose

Garden of Eden is a Raspberry Pi garden controller. The application exposes sensor and actuator APIs, a built-in web UI, MQTT integrations, automations, and a simulator for development without hardware.

## Main areas

- `app/`: application package, including sensors, integrations, shared libraries, and the web UI.
- `config.py`: environment and hardware configuration.
- `run.py`: application entry point.
- `mqtt.py`: MQTT control and integration process.
- `automations/`: light and pump automation definitions.
- `bin/`: installation, service, update, and operational scripts.
- `simulator/`: fake hardware and local service helpers.
- `tests/`: unit and integration tests.
- `docs/`: user, installation, maintenance, design, and integration documentation.

## Development checks

Create a development environment and install the declared test dependencies:

```bash
python3 -m venv .venv-dev
.venv-dev/bin/pip install -r requirements-dev.txt
```

Run the test suite:

```bash
.venv-dev/bin/python -m pytest
```

Run lint and formatting checks:

```bash
.venv-dev/bin/ruff check .
.venv-dev/bin/black --check .
```

The project uses Python 3.9 or newer. Hardware dependencies are stubbed by the tests where possible; hardware-only behavior should be validated on the Pi or with the simulator when appropriate.

## Hardware model selection

The `/system` endpoint reports the selected model and its hardware profile. Set `GARDYN_MODEL` in the Pi-local `.env` to explicitly choose one of the supported profiles: `gardyn 1.0`, `gardyn 2.0`, `gardyn 3.0`, `gardyn 4.0`, `gardyn studio`, or `gardyn studio 2`.

The two hardware lines differ in their physical layout. The **Home line** (1.0 through 4.0) is the max-yield architecture: 3 towers, 2 full-spectrum LED light bars, 2 cameras, 30 plant pods. The **Studio line** (Studio, Studio 2) is the trimmed profile for compact spaces: 2 towers, 1 light bar, 1 camera, 16 pods. Pod capacity and tower count follow the selected model automatically; set `POD_COUNT` or `POD_COLUMNS` in `.env` only for a unit that differs from its profile.

Without an override, the application infers the model family from the temperature/humidity sensor when possible. `DHT20` implies the Home 3.0 and `AM2320` implies Home 1.0/2.0. This is a best-effort inference, not a definitive identification, and it cannot separate the two lines at all: a Studio is also `DHT20`, so a Studio is inferred as a 3.0 until the model is set explicitly — either in `.env` or from the Settings card in the web UI.

The API reports temperatures in Celsius for integrations. The web UI converts air and PCB temperatures to Fahrenheit for display.

## Commit style

Use Conventional Commit subjects with lowercase types and an optional scope, for example:

```text
fix(web): close index file handle after serving
feat(integrations): add telemetry adapter
```

Keep commits focused and include tests or documentation when behavior changes.
