import logging
import argparse
import json
from datetime import datetime

"""
This module provides functionality to read temperature values from the AM2320 sensor 
using the adafruit_ahtx0 library. The CachedSensor class caches the readings for a 
specified duration to prevent redundant reads.
"""

import time
import board
import adafruit_ahtx0
import logging
import argparse
import json
from datetime import datetime
import busio
import adafruit_am2320

class AM2320Sensor():
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)

        self.sensor = adafruit_am2320.AM2320(i2c)

    def get_humidity(self):
        return self.sensor.relative_humidity


sensor = None

try:
   sensor = AM2320Sensor()
except:
    logging.info("Failed to initiate humidity sensor")

if __name__ == "__main__":
    """
    If the module is executed as a standalone script, it will return the temperature in a telegraf friendly format. 
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='Control a humidity sensor.')
    parser.add_argument('--log', action='store_true')
    args = parser.parse_args()


    try:
        humidity = sensor.get_humidity()
    except Exception as e:
        logging.info(f"Error: {e}")
    except KeyboardInterrupt:
        logging.info("Script interrupted.")

    if args.log:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            "timestamp": timestamp,
            "sensor": "Humidity",
            "value": humidity,
        }
        logging.info(json.dumps(log_entry))
        print(json.dumps(log_entry))
