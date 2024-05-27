# coding=utf-8
import smbus
from ina219 import INA219
from ina219 import DeviceRangeError
import time
from flask import jsonify, send_file
import argparse
import json
from datetime import datetime
import logging
import os

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
        except Exception as e:
            return {"error":str(e)}
    else:
        return {"error":"INA219 not found at address 0x40"}
    
    return data

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='Get pump stats.')
    parser.add_argument('--log', action='store_true')

    args = parser.parse_args()

    if args.log:
        pump_data = fetch_ina219_data()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            "timestamp": timestamp,
            "sensor": "Current",
            "bus_voltage": pump_data['Bus Voltage'],
            "bus_current": pump_data['Bus Current'],
            "power": pump_data['Power'],
            "shunt_voltage": pump_data['Shunt Voltage'],
        }
        logging.info(json.dumps(log_entry))
        print(json.dumps(log_entry))
    else:
        logging.info("No action specified. Use --log.")
