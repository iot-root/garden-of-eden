import smbus2
import time

class AM2320:
    def __init__(self, i2c_bus=1):
        self.bus = smbus2.SMBus(i2c_bus)
        self.address = 0x38

    def read(self):
        try:
            # Wake up the sensor
            self.bus.write_i2c_block_data(self.address, 0x00, [])
        except:
            pass

        time.sleep(0.01)  # wait for the sensor to wake up

        # Request data
        self.bus.write_i2c_block_data(self.address, 0x03, [0x00, 0x04])

        # Read the data
        data = self.bus.read_i2c_block_data(self.address, 0, 8)

        humidity = ((data[2] << 8) + data[3]) / 10.0
        temperature = ((data[4] << 8) + data[5]) / 10.0
        # Handle negative temperatures
        if temperature > 3276.7:
            temperature -= 6553.6
        return humidity, temperature


if __name__ == "__main__":
    sensor = AM2320()

    humidity, temperature = sensor.read()
    print(f"Humidity: {humidity}%")
    print(f"Temperature: {temperature}°C")
