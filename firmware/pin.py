import pigpio

class Pin:
  
  INPUT = pigpio.INPUT
  OUTPUT = pigpio.OUTPUT
  PWM = "PWM"

  def __init__(self, num, mode, freq=0):
    self.num = num
    self.mode = mode
    self.freq = freq
    self.gpio = pigpio.pi()
    if self.mode == Pin.PWM:
      assert self.freq != 0
      self.gpio.set_PWM_frequency(self.num, self.freq)
    else:
      self.gpio.set_mode(self.num, self.mode)

  def read(self):
    return self.gpio.read(self.num)

  def write(self, val):
    self.gpio.write(self.num, val)

class PWM(Pin):

  def __init__(self, num, freq):
    super().__init__(num, Pin.PWM, freq=freq)
  
  def read(self):
    return self.gpio.get_PWM_dutycycle(self.num)
  
  def write(self, duty):
    assert duty >= 0
    assert duty <= 255
    self.gpio.set_PWM_dutycycle(self.num, duty)
