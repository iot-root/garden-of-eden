"""Read relative humidity from the AM2320 (Gardyn 1.0/2.0) or DHT20 (Gardyn
3.0+) I2C sensor. Initialized lazily and re-probed on read failure (issue #57).
"""

import logging
import os
import sys
import time

import adafruit_ahtx0
import adafruit_am2320
import board

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import config

logger = logging.getLogger(__name__)


def _make_sensor():
    i2c = board.I2C()
    if config.SENSOR_TYPE == "AM2320":
        return adafruit_am2320.AM2320(i2c, address=0x5C)
    elif config.SENSOR_TYPE == "DHT20":
        return adafruit_ahtx0.AHTx0(i2c, address=0x38)
    raise ValueError(f"Unsupported sensor type: {config.SENSOR_TYPE!r}")


class HumiditySensor:
    """Resilient wrapper that (re)initializes the underlying sensor on demand."""

    def __init__(self):
        self._sensor = None
        try:
            self._sensor = _make_sensor()
        except Exception as exc:
            logger.error("Failed to initiate humidity sensor: %s", exc)

    def read(self):
        """Return relative humidity (%). Retries transient I2C errors and the
        DHT20's occasional bogus 0% reading; raises only if all attempts fail."""
        last_exc = None
        for attempt in range(3):
            if self._sensor is None:
                try:
                    self._sensor = _make_sensor()  # re-probe the bus
                except Exception as exc:
                    last_exc = exc
                    time.sleep(0.2)
                    continue
            try:
                value = self._sensor.relative_humidity
            except Exception as exc:  # transient [Errno 5] etc — drop handle, retry
                last_exc = exc
                self._sensor = None
                time.sleep(0.2)
                continue
            if value and value > 0:
                return value
            # Implausible 0% (collision/garbage) — re-measure.
            time.sleep(0.2)
        if last_exc:
            raise last_exc
        raise RuntimeError("humidity read returned 0% on every attempt")


humidity_sensor = HumiditySensor()

if __name__ == "__main__":
    # Standalone: print in a telegraf-friendly format.
    try:
        humidity = humidity_sensor.read()
        print(f"humidity, value={humidity:.2f}")
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Script interrupted.")
