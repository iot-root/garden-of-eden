from pin import PWM
from conf import LIGHT_PIN, LIGHT_FREQ

class Lights(PWM):
  def __init__(self):
    super().__init__(LIGHT_PIN, LIGHT_FREQ)
  
  def full(self):
    self.write(255)

  def medium(self):
    self.write(128)

  def off(self):
    self.write(0)
