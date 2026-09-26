# Known Issues

This list records confirmed limitations found during repository review. Keep it factual and remove entries when the underlying behavior is fixed.

## Sensor logging script

`bin/get-sensor-data.sh` is a legacy text-logging wrapper rather than a structured telemetry pipeline. It currently:

- assumes the runtime environment is at `venv/bin/python`;
- creates `/var/log/gardyn-data.log` with `sudo touch` but appends without `sudo`, which can fail for an unprivileged cron user;
- does not stop on sensor command failures, so failed reads can become empty log entries;
- is shown as a manual cron entry in `README.md` rather than being installed by `bin/setup.sh`.

The sensor drivers should be run through a consistently configured service or wrapper before relying on this log for monitoring.

## Manual API startup

`run.py` uses Flask's development server with `debug=True` and binds to all interfaces when run directly. The installed systemd service uses Waitress instead, but `python run.py` should be treated as a development-only path and not exposed on an untrusted network.

## Schedule application consistency

`app/sensors/schedule/schedule.py` persists the normalized schedule before writing the user's crontab. If the crontab write fails, the JSON state and active crontab can temporarily disagree. The API reports the failure, but the persisted schedule remains changed.

## Integration completeness

Alexa and ThingsBoard support are documented scaffolds. Alexa currently expects a Home Assistant bridge, and ThingsBoard validates configuration and logs telemetry intent without performing a network transport.

## Hardware acceptance

The test suite and simulator cover substantial application behavior, but real Pi acceptance checks are still required for sensor reads, camera capture, GPIO control, pigpiod availability, systemd startup, and Home Assistant MQTT discovery.

## Hardware stubs disable themselves on the Pi

`tests/_hwstub.py` installs fake `board`, `gpiozero`, `pigpio`, `smbus`, and
`ina219` modules, but only when the real Blinka `board` package is *not*
importable. On the Pi that import succeeds, so `install()` returns early and no
stubs are installed. The suite then runs against live hardware: it constructs
real `Light` and `Pump` objects, opens real pigpiod connections, and reads real
I2C devices.

The practical consequence is that running the suite on the Pi with the runtime
`venv` is a live hardware exercise, not a unit test run, and it is not
hermetic. A developer environment built from `requirements-dev.txt` does not
install `board`, so stubs apply there as intended. Run the suite off the Pi, or
in such an environment, and reserve on-Pi runs for deliberate hardware checks.

A related operational hazard: a stale `.venv` directory in the checkout can
survive from another machine. Its interpreter and console scripts are built for
a foreign architecture and fail with `bad interpreter` or `Exec format error`.
Nothing in the repository references `.venv`; the runtime uses `venv` and
development uses `.venv-dev`, so an unusable `.venv` is safe to delete.
