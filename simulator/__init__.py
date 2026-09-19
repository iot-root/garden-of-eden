"""Off-Pi hardware simulator.

Lets you run and manually test the full stack (web UI, REST API, and MQTT/Home
Assistant discovery) on a normal machine with no Raspberry Pi attached.

- ``simulator.fake_hardware.install()`` injects realistic, stateful fakes for the
  GPIO/I2C libraries into ``sys.modules`` (must run before importing ``app``).
- ``python -m simulator.serve`` runs the Flask app (web UI + REST) with fakes.
- ``python -m simulator.mqtt_sim`` runs the MQTT service with fakes against a
  local broker so Home Assistant can discover the simulated device.
"""
