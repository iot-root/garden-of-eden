# Telegraf / InfluxDB (issue #16)

Collect Gardyn telemetry into InfluxDB (or any Telegraf output) for dashboards
and history.

A ready-to-edit config ships at
[`services/telegraf/telegraf.conf`](../../services/telegraf/telegraf.conf).

## Setup

1. Install Telegraf on the Pi (or another host):
   ```bash
   sudo apt install telegraf
   ```
2. Copy the sample config:
   ```bash
   sudo cp services/telegraf/telegraf.conf /etc/telegraf/telegraf.d/gardyn.conf
   ```
3. Choose a collection method (both are in the file):
   - **MQTT consumer** (default): subscribes to the `gardyn/*` topics that
     `mqtt.py` already publishes. Nothing else to run.
   - **exec**: runs the driver CLIs directly; each prints InfluxDB line protocol
     (`temperature, value=22.5`). Useful without the MQTT service.
4. Point the `[[outputs.influxdb_v2]]` section at your InfluxDB and set
   `INFLUX_TOKEN`.
5. Restart Telegraf:
   ```bash
   sudo systemctl restart telegraf
   ```

Set `TELEGRAF_ENABLED=true` in `.env` to record that this integration is in use.
