import pigpio

class Pin:
  
  INPUT = pigpio.INPUT
  OUTPUT = pigpio.OUTPUT

  def __init__(self, num, status):
    self.num = num
    self.gpio = pigpio.pi()
    self.gpio.set_mode(self.num, status)

  def read(self):
    self.gpio.read(self.num)

  def write(self, val):
    self.gpio.write(self.num, val)