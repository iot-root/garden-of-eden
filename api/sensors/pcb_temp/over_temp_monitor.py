import time
import board
import adafruit_pct2075
from gpiozero import Button
from gpiozero.pins.pigpio import PiGPIOFactory

factory = PiGPIOFactory()
button = Button(25, pull_up=False, pin_factory=factory) # Pull down, use pigpio

i2c = board.I2C()  # uses board.SCL and board.SDA
pct = adafruit_pct2075.PCT2075(i2c, address=0x48)
pct.high_temperature_threshold = 36 # Set over_temp pin high when temp goes above this level
pct.temperature_hysteresis = 34     # Set over_temp pin to low after temp drops below this level
pct.high_temp_active_high = True    # Active high on alert 

logging.info("High temp alert active high? %s" % pct.high_temp_active_high)

def gpio_callback(channel):
    if button.is_pressed:
        logging.info("Trigger HIGH - Temperature: %.2f C" % pct.temperature)
    else:
        logging.info("Trigger LOW - Temperature: %.2f C" % pct.temperature)

# Set up the GPIO event detection
button.when_pressed = gpio_callback

try:
    while True:
        if button.is_pressed:
            logging.info("HIGH Temperature: %.2f C" % pct.temperature)
        else: 
            logging.info("LOW Temperature: %.2f C" % pct.temperature)
        time.sleep(0.5)

except KeyboardInterrupt:
    # Clean up pin settings on Ctrl+C
    button.close()
