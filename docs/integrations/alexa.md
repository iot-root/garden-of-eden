# Alexa (issue #82)

Control the Gardyn with Amazon Alexa ("Alexa, turn on the grow light").

**Recommended: bridge through Home Assistant.** Every actuator and sensor is
already exposed to Home Assistant via MQTT discovery, so you get Alexa support
without any custom code:

1. Set up [Home Assistant](../homeassistant/lovelace-example.yaml) with this
   project's MQTT integration (entities auto-discover).
2. Enable Alexa in HA via [Nabu Casa Cloud](https://www.nabucasa.com/) (easiest)
   or the [manual Alexa Smart Home skill](https://www.home-assistant.io/integrations/alexa.smart_home/).
3. Expose the `light.gardyn_*` / `light.gardyn_*_pump` entities to Alexa.

**Alternative: direct smart-home skill.** Build a custom Alexa Smart Home skill
backed by an AWS Lambda that publishes to the MQTT command topics
(`gardyn/light/command`, `gardyn/pump/command`). The Lambda lives outside this
repo; `ALEXA_ENABLED` is reserved for any future in-process glue.
