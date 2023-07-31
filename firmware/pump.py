from pin import Pin
from conf import PUMP_PIN

class Pump(Pin):
  def __init__(self):
    super().__init__(PUMP_PIN, Pin.OUTPUT)
  
  def start(self):
    self.write(1)

  def stop(self):
    self.write(0)
