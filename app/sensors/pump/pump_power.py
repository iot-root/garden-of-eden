# coding=utf-8
import smbus
from ina219 import INA219
from ina219 import DeviceRangeError
import time

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
                'BusVoltage': ina.voltage(),
                'BusCurrent': None,
                'Power': None,
                'ShuntVoltage': ina.shunt_voltage(),
            }
            data['Bus Current'] = ina.current()
            data['Power'] = ina.power()
        except DeviceRangeError as e:
            data['error'] = str(e)
    else:
        data['error'] = "INA219 not found at address 0x40"
    
    return data

if __name__ == '__main__':
    """
    If the module is executed as a standalone script, it will return the temperature in a telegraf friendly format. 
    """
    try:
        sensor_data = fetch_ina219_data()
        print("INA219 Sensor Data:")
        for key, value in sensor_data.items():
            print(f"{key}, value={value}")
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Script interrupted.")
