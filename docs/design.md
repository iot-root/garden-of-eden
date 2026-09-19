# Architecture & Design Decisions

Covers the overall architecture (#26) and the pi-zero / pigpio rationale (#43).

## Big picture

Three control surfaces sit on top of **one driver layer**:

```
                    ┌──────────────────────────────┐
   Home Assistant ──┤ mqtt.py  (MQTT service)       │
                    ├──────────────────────────────┤
   App / curl    ───┤ run.py + app/ (Flask REST)    ├── app/sensors/*  ── pigpiod / I2C ── hardware
                    ├──────────────────────────────┤      (drivers)
   Cron / shell  ───┤ driver CLIs (python …/*.py)   │
                    └──────────────────────────────┘
```

- **Drivers** (`app/sensors/<name>/<name>.py`) own all hardware access. Behavior
  changes belong here, not in a single entry point.
- **Shared helpers** live in `app/lib/`: `hardware.py` (one pigpio pin factory +
  model detection), `logging_config.py`, `lib.py` (`check_sensor_guard`),
  `water.py`, `grow.py`, `state.py`.
- **REST** assembles per-sensor Flask blueprints in `app/__init__.py:create_app`.
- **MQTT** (`mqtt.py`) publishes Home Assistant discovery + telemetry and handles
  commands and the physical button.

## Why pigpio (not RPi.GPIO)

The grow light and pump are driven with **hardware-timed PWM**. RPi.GPIO's
software PWM jitters and flickers the LED; `pigpio` uses DMA-based PWM that is
stable at the light's 8 kHz and the pump's 50 Hz. pigpio runs as a daemon
(`pigpiod`), which also enables the Docker story: containers set
`PIGPIO_HOST`/`PIGPIO_PORT` and talk to the daemon on the host instead of needing
privileged GPIO access. A **single shared `PiGPIOFactory`** (`app/lib/hardware.py`)
is injected into every driver so there's one daemon connection per process.

## Why a Pi Zero 2

The original Pi Zero W is single-core and struggles with concurrent MQTT +
camera capture + Flask. The Zero 2 W is a drop-in upgrade (same form factor,
quad-core) — see [pizero2-upgrade.md](pizero2-upgrade.md).

## Resilience choices

- Drivers initialize **lazily** and **re-probe** on read failure, so a transient
  I2C glitch doesn't permanently disable a sensor (#57).
- `check_sensor_guard` distinguishes "not initialized" (400) from "hardware
  unavailable" (503) so clients aren't told a disconnected sensor succeeded.
- Actuator + grow state is persisted and restored on boot for power-loss
  recovery (#3); `mqtt.py` turns the pump off cleanly on SIGTERM.
