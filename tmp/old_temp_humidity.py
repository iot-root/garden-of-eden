# coding=utf-8
import posix
from fcntl import ioctl
import time

class AM2320:
  # I2C_ADDR = 0x5c
  I2C_ADDR = 0x38
  I2C_SLAVE = 0x0703

  def __init__(self, i2cbus = 1):
    self._i2cbus = i2cbus

  @staticmethod
  def _calc_crc16(data):
    crc = 0xFFFF
    for x in data:
      crc = crc ^ x
      for bit in range(0, 8):
        if (crc & 0x0001) == 0x0001:
          crc >>= 1
          crc ^= 0xA001
        else:
          crc >>= 1
    return crc

  @staticmethod
  def _combine_bytes(msb, lsb):
    return msb << 8 | lsb


  def readSensor(self):
    try:
      fd = posix.open("/dev/i2c-{}".format(self._i2cbus), posix.O_RDWR)

      ioctl(fd, self.I2C_SLAVE, self.I2C_ADDR)
    except:
      print("Somethign happened 1")
      pass
    
    # wake AM2320 up, goes to sleep to not warm up and affect the humidity sensor
    # This write will fail as AM2320 won't ACK this write
    try:
      posix.write(fd, b'\x00')
    except:
      print("Somethign happened 2")
      pass
    time.sleep(0.001)  #Wait at least 0.8ms, at most 3ms

    # write at addr 0x03, start reg = 0x00, num regs = 0x04 */
    posix.write(fd, b'\x03\x00\x04')
    time.sleep(0.0016) #Wait at least 1.5ms for result

    # Read out 8 bytes of result data
    # Byte 0: Should be Modbus function code 0x03
    # Byte 1: Should be number of registers to read (0x04)
    # Byte 2: Humidity msb
    # Byte 3: Humidity lsb
    # Byte 4: Temperature msb
    # Byte 5: Temperature lsb
    # Byte 6: CRC lsb byte
    # Byte 7: CRC msb byte
    data = bytearray(posix.read(fd, 8))

    # Check data[0] and data[1]
    if data[0] != 0x03 or data[1] != 0x04:
      posix.close(fd)
      raise Exception("First two read bytes are a mismatch")

    # CRC check
    if self._calc_crc16(data[0:6]) != self._combine_bytes(data[7], data[6]):
      posix.close(fd)
      raise Exception("CRC failed")

    # Temperature resolution is 16Bit,
    # temperature highest bit (Bit15) is equal to 1 indicates a
    # negative temperature, the temperature highest bit (Bit15)
    # is equal to 0 indicates a positive temperature;
    # temperature in addition to the most significant bit (Bit14 ~ Bit0)
    # indicates the temperature sensor string value.
    # Temperature sensor value is a string of 10 times the
    # actual temperature value.
    temp = self._combine_bytes(data[4], data[5])
    if temp & 0x8000:
      temp = -(temp & 0x7FFF)
    temp /= 10.0

    humi = self._combine_bytes(data[2], data[3]) / 10.0
    posix.close(fd)

    return temp, humi

if __name__ == '__main__':
    try:
        am2320 = AM2320(1)
        # read twice because the first one always the wrong one?
        t, h = am2320.readSensor()
        t, h = am2320.readSensor()
        print("[{}]Temperature:{}, Humidity:{}".format(time.ctime(time.time()),t,h))
        

    except Exception as e:
        print(e)
        print("[{}]Error when reading the temperature & humidity data".format(time.ctime(time.time())))
        