from pin import Pin

class Pump(Pin):
  def __init__(self):
    super().__init__(24, Pin.OUTPUT)
  
  def start(self):
    self.write(1)

  def stop(self):
    self.write(0)
