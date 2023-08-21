# coding=utf-8
from ina219 import INA219
from ina219 import DeviceRangeError

SHUNT_OHMS = 0.08

def fetch_ina219_data():
    ina = INA219(SHUNT_OHMS)
    ina.configure()
    
    data = {
        'Bus Voltage': ina.voltage(),
        'Bus Current': None,
        'Power': None,
        'Shunt Voltage': ina.shunt_voltage(),
    }
    
    try:
        data['Bus Current'] = ina.current()
        data['Power'] = ina.power()
    except DeviceRangeError as e:
        data['error'] = str(e)
    
    return data
