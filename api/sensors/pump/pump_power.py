# coding=utf-8
import smbus
from ina219 import INA219
from ina219 import DeviceRangeError
import time
import logging
from flask import jsonify


SHUNT_OHMS = 0.08

def is_ina219_present(address):
    try:
        bus = smbus.SMBus(1)  # Use SMBus(0) for older versions of Raspberry Pi
        bus.read_byte_data(address, 0)  # Try to read a byte from the specified address
        return True  # If no exception is raised, the device is present
    except Exception:
        return False

def fetch_ina219_data():
    data = {}
    if is_ina219_present(0x40):  # Check if the INA219 is present at address 0x40
        try:
            ina = INA219(SHUNT_OHMS, address=0x40)  # Specify the INA219's address
            ina.configure()
            time.sleep(1)
            data = {
                'Bus Voltage': ina.voltage(),
                'Bus Current': ina.current(),
                'Power': ina.power(),
                'Shunt Voltage': ina.shunt_voltage(),
            }
        except DeviceRangeError as e:
            return {"error":str(e)}
    else:
        return {"error":"INA219 not found at address 0x40"}
    
    return data

if __name__ == '__main__':
    """
    If the module is executed as a standalone script, it will return the temperature in a telegraf friendly format. 
    """
    try:
        sensor_data = fetch_ina219_data()
        logging.info("INA219 Sensor Data:")
        for key, value in sensor_data.items():
            logging.info(f"{key}, value={value}")
    except Exception as e:
        logging.info(f"Error: {e}")
    except KeyboardInterrupt:
        logging.info("Script interrupted.")
