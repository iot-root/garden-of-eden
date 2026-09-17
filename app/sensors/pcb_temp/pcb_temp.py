import os
import sys

import adafruit_pct2075
import board

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import config


def get_pcb_temperature():
    i2c = board.I2C()  # uses board.SCL and board.SDA
    pct = adafruit_pct2075.PCT2075(i2c, address=config.PCB_TEMP_ADDRESS)

    return pct.temperature


if __name__ == "__main__":
    """
    If the module is executed as a standalone script, it will return the pcb_temp in a telegraf friendly format.
    """
    try:
        pcb_temp = get_pcb_temperature()
        print(f"pbc_temp, value={pcb_temp:.2f}")
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Script interrupted.")
