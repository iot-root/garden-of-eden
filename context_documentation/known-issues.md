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
