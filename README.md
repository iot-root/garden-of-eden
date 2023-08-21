<hr>

<img src="docs/banner.svg" width="800px">

# Gardyn-of-eden

Truly own that which is yours!

Work is in progress, but we should be picking up some steam here to give the DYI community the features you deserve.

If you are interested in collaborating please review the [CONTRIBUTORS](CONTRIBUTORS.md) for commit styling guides. 

Checkout the [Electrical Diagrams](#electrical-diagrams)

## Quick Run

usage `python run.py` will launch the flask api.

**Physical Testing of Rest API**

run `./bin/api-test.sh` to cycle through the various endpoint tests.

**Unit Tests**

run `python -m unittest -v`

or for example: `python tests/test_distance.py`


**Individual sensor controls**

```
python app/sensors/distance/distance.py
Measured Distance: 31.84 cm

python app/sensors/pump/pump.py
Setting pump frequency to 50
Turning pump on
Setting pump 1duty_cycle_percentage to 30
Turning pump off

python app/sensors/light/light.py
Setting light frequency to 8000
Turning light on
Setting light duty_cycle_percentage to 50
Turning light off
```


## Milestones
- [ ] [Hardware Interface](https://github.com/iot-root/garden-of-eden/milestone/6)
    - [x] [pump](https://github.com/iot-root/garden-of-eden/issues/33)
    - [x] [lights](https://github.com/iot-root/garden-of-eden/issues/34)
    - [x] [temp & humidty](https://github.com/iot-root/garden-of-eden/issues/35)
    - [ ] [button](https://github.com/iot-root/garden-of-eden/issues/36)
    - [x] [motor current & overtemp](https://github.com/iot-root/garden-of-eden/issues/37)
    - [x] [distance/waterlevel](https://github.com/iot-root/garden-of-eden/issues/38)
    - [ ] [camera](https://github.com/iot-root/garden-of-eden/issues/40)
- [x] [Rest API](https://github.com/iot-root/garden-of-eden/milestone/7)
- [ ] [Dashboard](https://github.com/iot-root/garden-of-eden/milestone/8)

## ToDo
- [ ] test compatibility pi models: pi-zero, pi-zero 2
- [ ] simple scheduling interface...
- [x] Reverse engineer and document hardware, software
    - [x] [Electrical Diagrams](#electrical-diagrams)
- [ ] document API endpoints
- [ ] Figure out temp humidity and onboard motor sensor via i2c
- [ ] Add homeassistant support
- [ ] Rewrite for to collect data for graphs and analytics
- [ ] Dockerize?

## Design Decisions

Reading sensor values with inheritly long delays and responding to the REST API.

```
<garden-of-eden>
├── run.py
├── app
│   ├── __init__.py
│   └── sensors
│       ├── config.py
│       ├── distance
│       │   ├── distance.py
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── __init__.py
│       ├── light
│       │   ├── __init__.py
│       │   ├── light.py
│       │   └── routes.py
│       └── pump
│           ├── __init__.py
│           ├── pump.py
│           └── routes.py
└── tests
    ├── __init__.py
    ├── test_distance.py
    ├── test_light.py
    └── test_pump.py
```

## Getting Started

### Recomendations

**Pi Zero 2**
I replaced my pi zero with a pi-zero-2, it is signifantly faster and I can use VS Code remote server to edit files and debug the python code remotely. 
> Buy one `without` a header, you will need to solder one on in the opposite direction.
 
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
