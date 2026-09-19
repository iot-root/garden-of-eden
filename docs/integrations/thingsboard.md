# ThingsBoard (issue #24)

Forward telemetry to a [ThingsBoard](https://thingsboard.io/) instance.

**Status:** scaffold. `app/integrations/thingsboard.py` validates config and logs
intent; the transport call is marked `TODO` pending a device token.

## Setup

1. In ThingsBoard, create a device and copy its **access token**.
2. Configure `.env`:
   ```
   THINGSBOARD_ENABLED=true
   THINGSBOARD_HOST=your-thingsboard-host
   THINGSBOARD_TOKEN=your-device-access-token
   ```
3. Implement the transport in `publish_telemetry()` (HTTP example is in the
   docstring), then call it from the telemetry publishers in `mqtt.py`
   (`publish_temperature`, `publish_humidity`, etc.).

ThingsBoard accepts telemetry via:
- **HTTP:** `POST https://<host>/api/v1/<token>/telemetry` with a JSON body.
- **MQTT:** publish JSON to `v1/devices/me/telemetry` authenticated with the
  token as the MQTT username.
