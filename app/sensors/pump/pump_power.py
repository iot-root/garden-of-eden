# coding=utf-8
from ina219 import INA219
from ina219 import DeviceRangeError

SHUNT_OHMS = 0.08

def fetch_ina219_data():
    try:
        ina = INA219(SHUNT_OHMS)
        ina.configure()
            
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

        #  print(f"temperature, value={temperature:.2f}")
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Script interrupted.")




