# Upgrading to a Raspberry Pi Zero 2 W (issue #66)

The Gardyn ships with a Pi Zero W (single-core). The **Pi Zero 2 W** is a
pin- and form-compatible drop-in with a quad-core CPU that comfortably handles
MQTT + camera capture + the REST API at once.

## Steps

1. **Flash a fresh card** with Raspberry Pi OS (Lite is plenty) using the
   [Raspberry Pi Imager](https://www.raspberrypi.com/software/). In the imager's
   advanced options, set the hostname, enable SSH, and configure Wi‑Fi.
2. **Swap the board.** Power off the Gardyn, remove the Zero W from the internal
   carrier, and seat the Zero 2 W in its place (same headers/camera connector).
3. **Reinstall the software:**
   ```bash
   git clone https://github.com/iot-root/garden-of-eden.git
   cd garden-of-eden
   cp .env-dist .env && nano .env      # set MQTT + identity
   ./bin/setup.sh
   ```
4. **Verify:** `curl localhost:5000/system` should report your model, and
   `sudo systemctl status mqtt.service` should be active.

## Notes

- The Zero 2 W runs warmer; the PCB over-temp thresholds (`OVER_TEMP_HIGH` /
  `OVER_TEMP_HYSTERESIS`) are configurable in `.env` if needed.
- No wiring changes are required — pin assignments are identical and now live in
  `config.py` (overridable via `.env`).
