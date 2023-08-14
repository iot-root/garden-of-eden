# Gardyn-of-eden
Truly own that which is yours!

Working in progress, but we should be picking up some steam here to give the DYI community the featuers you deserve.

If you are interested in collaborating please review the [CONTRIBUTORS](CONTRIBUTORS.md) for commit styling guides. 

## Milestones
- [ ] [Sensor Interface](https://github.com/iot-root/gardyn-of-eden/milestone/6)
- [ ] [Rest API](https://github.com/iot-root/gardyn-of-eden/milestone/7)
- [ ] [Dashboard](https://github.com/iot-root/gardyn-of-eden/milestone/8)

## ToDo
- [x] Reverse engineer and document hardware, software
- [ ] Add homeassistant support
- [ ] Rewrite for to collect data for graphs and analytics
- [ ] Dockerize?

## System Overview

Depending on the system you have, here is a breakdown of the hardware.

Notes: 
- GPIO num is different than pin number. See (https://pinout.xyz/)

### Lights

LED full spectrum lights, will do more technical research for optimal PWM driving.

Method
- Lights are driven by PWM duty and a frequency of 8 kHz.

Pins
- [GPIO-18](https://pinout.xyz/pinout/pin12_gpio18/)

### Pump

Method:
- The pump is driven by PWM with max duty of 30% and frequency of 50 Hz
- There is a current sensor to measure pump draw and a overtemp sensor to determine if board monitor PCB temp.

Pins:
- [GPIO-24](https://pinout.xyz/pinout/pin18_gpio24/)

Notes:
- Pump duty cycle is limited, likely full on is too much current draw for the system. 

### Camera

Two USB cameras. 

Method:
- image capture with fswebcam

Devices:
- /dev/video0
- /dev/video1

### Water Level Sensor

Uses the ultrasonic distance sensor DYP-A01-V2.0.

Pins:
- [GPIO-19](https://pinout.xyz/pinout/pin35_gpio19/): water level in
- [GPIO-26](https://pinout.xyz/pinout/pin35_gpio26/): water level out

Method:
- Uses time between the echo and response to deterine the distances.

References:
- https://www.google.com/search?q=DYP-A01-V2.0
- https://www.dypcn.com/uploads/A02-Datasheet.pdf

### Temp & Humidty Sensor

### Momentary Button

`<section incomplete>`

## Electrical Diagrams

Incase you need to troubleshoot any problems with your system.

### Sensors
<img src="docs/pcb1.png" width="800px">

### Power and Header
<img src="docs/pcb2.png" width="800px">