# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Firmware/control software for a **Gardyn** hydroponic system running on a Raspberry Pi (Zero W / Zero 2 W) inside the unit. It talks to physical hardware over GPIO and I2C: lights (PWM), water pump, distance/water-level sensor, temperature & humidity, PCB temp, pump power monitor, USB cameras, and a momentary button.

It exposes three control surfaces over the **same sensor drivers**:
- **MQTT** (`mqtt.py`) — long-running service, Home Assistant auto-discovery, runs as `mqtt.service`.
- **Flask REST API + web UI** (`run.py` + `app/`) — served by waitress as `garden-api.service`.
- **CLI** — each driver module is runnable directly with argparse flags (see below).

## Running & development

This code only fully runs **on the Pi** — it imports `gpiozero`, `pigpio`, `adafruit_*`, etc. and requires the `pigpiod` daemon plus I2C hardware. Most logic cannot be exercised on a dev laptop; rely on the unit tests (which stub the hardware) for off-Pi work.

```bash
# One-time Pi setup: apt deps, venv, I2C enable, sensor detection, symlinks,
# systemd services and the nightly auto-update timer. Idempotent.
./bin/setup.sh --dry-run          # preview every system change; changes nothing
./bin/setup.sh

source venv/bin/activate          # all commands below assume the venv is active

python run.py                     # Flask dev server on 0.0.0.0:5000
python mqtt.py                    # MQTT service (normally run via systemd)
```

### Tests (run off-Pi)

CI and local tests run **without hardware**: `tests/_hwstub.py` (loaded by `tests/__init__.py`) injects fake `board`/`gpiozero`/`adafruit_*`/`pigpio`/`smbus` modules into `sys.modules`, but only when the real libs are absent.

```bash
python -m venv .venv-dev && .venv-dev/bin/pip install -r requirements-dev.txt
# CI gate — note the -t . so the tests PACKAGE (and its stub bootstrap) loads,
# while app/ is not scanned as test modules:
python -m unittest discover -t . -s tests -p 'test_*.py'
ruff check . && black --check .
```

Because the stub bootstrap lives in the `tests` package `__init__`, plain `python -m unittest` (which imports `app` directly) fails off-Pi — always use the `discover -t . -s tests` form above.

### Manual checks

```bash
./bin/api-test.sh                 # curls every REST endpoint (needs the API running)
# Run a driver directly (each has its own __main__ + argparse):
python app/sensors/light/light.py [--on] [--off] [--brightness INT] [--ramp-minutes INT]
python app/sensors/pump/pump.py [--on] [--off] [--speed INT]
python app/sensors/distance/distance.py
```

Symlinks `light`, `water` and `garden-update` (created by setup.sh → `bin/light.sh`, `bin/water.sh`, `bin/update.sh`) are convenience CLI wrappers on the Pi. They export `PYTHONPATH`, so the drivers they call find the root `config.py`.

## Architecture

### Sensor module pattern (the core convention)
Every sensor lives in `app/sensors/<name>/` and follows the same shape:
- `<name>.py` — the hardware driver: a class (e.g. `Light`, `Pump`, `Distance`) or function, plus a `__main__`/argparse block so it's runnable standalone. Drivers accept a `pin_factory` so callers can inject `PiGPIOFactory`.
- `routes.py` — a Flask `Blueprint` that instantiates the driver once and wraps each route with the `check_sensor_guard` decorator.
- `__init__.py`.

`app/__init__.py` (`create_app`) registers each blueprint under its own `url_prefix`: sensors (`/light`, `/pump`, `/distance`, `/temperature`, `/humidity`, `/pcb-temp`) plus `/camera`, `/schedule`, `/grow`, `/pods`, `/system`, a `/health` endpoint, and the built-in web UI at `/` (`app/web/`, a self-contained `index.html` served by `web_blueprint`). Adding a sensor = new folder following this pattern + one `register_blueprint` line. `create_app` also applies CORS and registers optional API-key auth (`_register_auth`, active only when `GARDEN_API_KEY` is set; localhost, `/`, `/health` and `/static` bypass it so the page can load and prompt for a key).

### Shared helpers (`app/lib/`)
- `hardware.py` — **`get_pin_factory()`** returns the one shared `PiGPIOFactory` (honors `PIGPIO_HOST`/`PIGPIO_PORT` for Docker); **`detect_model()`** infers the Gardyn model from I2C addresses.
- `lib.py` — `check_sensor_guard(sensor, name)`: 400 if the sensor is `None` (failed init), **503** if the handler raises (hardware unavailable), 400 on `ValueError`.
- `logging_config.py` — `configure_logging()` used by `run.py`, `mqtt.py`, CLIs (level via `LOG_LEVEL`).
- `water.py` (`is_water_low`, tank geometry), `grow.py` (grow-cycle state + reminders), `state.py` (actuator state persistence for power-loss recovery), `persist.py` (atomic JSON writes), `pods.py` + `plants.json` (pod inventory behind `/pods`).

Route drivers are instantiated at import inside a `try/except` → `None` on failure, so the app imports off-Pi and `check_sensor_guard` handles the degraded case.

### Configuration is centralized
All pins, I2C addresses, thresholds, file paths, and feature flags live in `config.py` (env-driven, hex-aware int parsing) and are documented in `.env-dist`. Drivers default their pins/addresses from `config.*` — don't hardcode. `MAX_PUMP_RUN_SECONDS` (900) is the pump's hard run-time cap and is read by the API, MQTT, the schedule compiler and `bin/water.sh`.

### Three entry points, one driver layer
`mqtt.py`, `run.py`/`app/`, and the per-driver CLIs all import the **same** driver classes from `app/sensors/*`. Behavior changes (e.g. how the pump ramps speed) belong in the driver, not in any single entry point.

### mqtt.py specifics
- Uses the shared `get_pin_factory()` and `configure_logging()`.
- Physical **button** (`gpiozero.Button`, `BUTTON_PIN`): single press → toggle light, double → toggle pump, long press (`when_held`) → event only. All presses publish to `<base>/button/event` as JSON `{"event_type": ...}` and are exposed as an HA `event` entity (#78).
- Publishes **Home Assistant MQTT discovery** (`send_discovery_messages`), reporting `detect_model()` as the device model. Topic base `BASE_TOPIC`.
- Publishes telemetry on a timer plus grow-cycle stage/reminders; water-low logic uses `app.lib.water.is_water_low`.
- **Power-loss recovery**: restores actuator state on connect (`restore_actuator_state`), persists state on every toggle (`app.lib.state`), and turns the pump off on SIGTERM/SIGINT (`graceful_shutdown`).

### Simulator (off-Pi)
`simulator/` runs the full stack with realistic fake hardware. `fake_hardware.install()` injects stateful fakes into `sys.modules` (distinct from `tests/_hwstub.py`, which is bare mocks for unit tests) and must run before importing `app`. `python -m simulator.serve` serves the web UI + REST (reloader off; camera returns a placeholder JPEG; **crontab is sandboxed** so schedules never touch the host). `python -m simulator.mqtt_sim` runs `mqtt.py` via `runpy` against a local broker for Home Assistant testing. `tests/test_discovery.py` validates HA discovery offline; `tests/test_integration.py` smoke-tests every GET route.

### Packaging, services & CI
- `Dockerfile` + `docker-compose.yml` run the API and MQTT service in containers, talking to a host `pigpiod` via `PIGPIO_HOST`. `requirements.txt` is Pi/runtime deps; `requirements-dev.txt` is pure-Python for CI.
- `bin/setup.sh` installs `mqtt.service`, `garden-api.service` (waitress on :5000), `garden-boot-indicator.service` (pulses the lights at power-on) and `garden-autoupdate.timer` (~03:30, `bin/autoupdate.sh` fast-forwards and restarts only when the branch moved). `bin/update.sh` (`garden-update`) updates in place; `bin/uninstall.sh` reverses the install.
- `.github/workflows/ci.yml` (ruff + black + unittest on 3.9/3.11) and `release-please.yml` (changelog/versioning from Conventional Commits). PR conventions live in `CONTRIBUTORS.md`.

## Hardware notes that affect code

- Requires the **pigpiod** daemon; drivers use `PiGPIOFactory` rather than the default gpiozero pin factory. `mqtt.service` depends on `pigpiod.service`.
- I2C device addresses are meaningful: PCT2075 `0x48` (PCB temp), INA219 `0x40` (pump power), DHT20 `0x38`, AM2320 `0x5c`. The AM2320 needs a wakeup sequence and won't show in a plain `i2cdetect`.
- `SENSOR_TYPE` (AM2320 for Gardyn 1.0/2.0, DHT20 for 3.0+) is auto-detected by `setup.sh` from the I2C address.
- Targets **Python 3.9+** (`pyproject.toml` and CI); pinned deps in `requirements.txt` are chosen for ARM/Pi compatibility, including armv6 (Pi Zero W) — be cautious bumping versions.
- Constructing a gpiozero device writes to its pin, and closing one releases it. Anything that builds a driver in a short-lived process can therefore change what the hardware is doing.

## Commit conventions

Conventional Commits (see `CONTRIBUTORS.md`): `<type>(<scope>): <description>` where type ∈ `feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert`, `!` for breaking changes with a `BREAKING CHANGE:` footer. One issue per PR, linked with `Closes #<issue>`.
