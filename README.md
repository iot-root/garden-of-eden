# Gardyn-of-eden
Truly own that which is yours!

# Code structure

## Pin

Class Pin has the common usage of any Raspberry PI pins

It can be used to read and write the values

To control a device create a subclass that initiated the pin mode and the number

Use `self.read()` to read the value for an input pin

Use `self.write(x)` to write the value `x` for an output pin.

# Hardware

## Pump

The pump is on pin 24

to start or stop the pump
```python
gpio = pigpio.pi()
gpio.set_mode(24, pigpio.OUTPUT)
gpio.write(24, 0) # stops the pump
gpio.write(24, 1) # starts the pump
```

## ToDo
- [ ] Reverse engineer and document hardware, software
- [ ] Add homeassistant support
- [ ] Rewrite for to collect data for graphs and analytics
- [ ] Dockerize?




