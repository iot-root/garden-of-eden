# External Integrations

Optional integrations, each gated by a flag in `.env`. They are scaffolds:
everything achievable on-device works out of the box; integrations needing
external accounts/keys are wired to clear extension points and documented here.

| Integration | Flag(s) | Status | Doc |
|-------------|---------|--------|-----|
| Home Assistant | (always on via MQTT) | Full | [../homeassistant/lovelace-example.yaml](../homeassistant/lovelace-example.yaml) |
| Telegraf / InfluxDB | `TELEGRAF_ENABLED` | Sample config shipped | [telegraf.md](telegraf.md) |
| ThingsBoard | `THINGSBOARD_ENABLED`, `THINGSBOARD_HOST`, `THINGSBOARD_TOKEN` | Scaffold | [thingsboard.md](thingsboard.md) |
| Alexa | `ALEXA_ENABLED` | Scaffold (HA bridge recommended) | [alexa.md](alexa.md) |
