"""Amazon Alexa integration (issue #82) — scaffold.

Two viable approaches, neither requiring changes to the core control code:

1. **Home Assistant bridge (recommended).** Because every actuator/sensor is
   already exposed to Home Assistant via MQTT discovery, the simplest path is to
   enable HA's Alexa Smart Home integration (Nabu Casa or a custom skill). No
   code here is required — see docs/integrations/alexa.md.

2. **Direct smart-home skill.** A custom Alexa Smart Home skill backed by an AWS
   Lambda that publishes to the same MQTT command topics (e.g.
   ``gardyn/light/command``). The Lambda handler would live outside this repo.

``ALEXA_ENABLED`` is provided so future in-process glue (e.g. a local skill
endpoint) can be toggled. Currently a documented no-op.
"""

import config


def is_enabled():
    return bool(config.ALEXA_ENABLED)
