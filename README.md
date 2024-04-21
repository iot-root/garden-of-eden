<img src="docs/_banner.svg" width="800px">

# Garden of Eden

Truly own that which is yours!

Work is in progress, but we should be picking up some steam here to give the DYI community the features you deserve.

If you are interested in collaborating please review the [CONTRIBUTORS](CONTRIBUTORS.md) for commit styling guides.

# Table of Contents

- [Garden of Eden](#garden-of-eden)
- [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Testing](#testing)
    - [Individual sensor controls](#individual-sensor-controls)
    - [Recommendations](#recommendations)
      - [Upgrading the Pi Zero 2](#upgrading-the-pi-zero-2)
  - [System Overview](#system-overview)
    - [Air Temp \& Humidty Sensor](#air-temp--humidty-sensor)
    - [Pump Power Monitor](#pump-power-monitor)
    - [PCB Temp Sensor](#pcb-temp-sensor)
    - [Lights](#lights)
      - [Method](#method)
      - [Pins](#pins)
    - [Pump](#pump)
      - [Method](#method-1)
      - [Pins](#pins-1)
    - [Camera](#camera)
      - [Method](#method-2)
      - [Devices](#devices)
    - [Water Level Sensor](#water-level-sensor)
      - [Pins](#pins-2)
      - [Method](#method-3)
      - [References](#references)
    - [Momentary Button](#momentary-button)
  - [Design Decisions](#design-decisions)
    - [Python Version 3.6 \>=](#python-version-36-)
    - [Delays in Reading Temp/Humidity data](#delays-in-reading-temphumidity-data)
    - [GPIO](#gpio)
  - [Rest API](#rest-api)
  - [File Structure](#file-structure)
  - [Electrical Diagrams](#electrical-diagrams)
    - [Sensors](#sensors)
    - [Power and Header](#power-and-header)
  - [Milestones](#milestones)
  - [TODO](#todo)
  - [Notes](#notes)

## Getting Started

```bash
# clone repo
git clone git@github.com:iot-root/garden-of-eden.git
cd garden-of-eden 

# activate the environment and install dependencies
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
pip freeze > requirements.txt
./bin/setup.sh

# ensure the pigpiod daemon is running
sudo systemctl start pigpiod

# launch the flask api
python run.py
```

### Testing

```bash
# REST endpoints
./bin/api-test.sh

# unit test
python -m unittest -v

# individual tests
python tests/test_distance.py
```

### Individual sensor controls

```bash
$ python app/sensors/distance/distance.py
Measured Distance: 31.84 cm

$ python app/sensors/pump/pump.py
Setting pump frequency to 50
Turning pump on
Setting pump 1duty_cycle_percentage to 30
Turning pump off

$ python app/sensors/light/light.py
Setting light frequency to 8000
Turning light on
Setting light duty_cycle_percentage to 50
Turning light off
```

### Recommendations

#### Upgrading the Pi Zero 2

For better performance, the Pi Zero can be replaced with a Pi Zero 2. This will enable the use of VS Code Remote Server to edit files and debug the python code remotely. The VS Code remote server uses OpenSSH and the minimum architecture is ARMv7.

> Buy one **without** a header, you will need to solder one on in the opposite direction.

## System Overview

Depending on the system you have, here is a breakdown of the hardware.

Notes:

- GPIO num is different than pin number. See (<https://pinout.xyz/>)

### Air Temp & Humidty Sensor

- temp/humidity sensor AM2320 at address of `0x38`

### Pump Power Monitor

- motor power usage sensor INA219 at address of `0x40`

### PCB Temp Sensor

- pcb temp sensor PCT2075 at address `pf 0x48`

When you run `sudo i2cdetect -y 1`, you should see something like:

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- 38 -- -- -- -- -- -- --
40: 40 -- -- -- -- -- -- -- 48 -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
```

### Lights

LED full spectrum lights.

#### Method

- Lights are driven by PWM duty and a frequency of 8 kHz.

#### Pins

- [GPIO-18 | PIN-12](https://pinout.xyz/pinout/pin12_gpio18/)

### Pump

#### Method

- The pump is driven by PWM with max duty of 30% and frequency of 50 Hz
- There is a current sensor to measure pump draw and a overtemp sensor to determine if board monitor PCB temp.

#### Pins

- [GPIO-24 | PIN-18](https://pinout.xyz/pinout/pin18_gpio24/)

Notes:

- Pump duty cycle is limited, likely full on is too much current draw for the system.

### Camera

Two USB cameras.

#### Method

- image capture with fswebcam

#### Devices

- /dev/video0
- /dev/video1

### Water Level Sensor

Uses the ultrasonic distance sensor DYP-A01-V2.0.

#### Pins

- [GPIO-19 | PIN-35](https://pinout.xyz/pinout/pin35_gpio19/): water level in (trigger)
- [GPIO-26 | PIN-37](https://pinout.xyz/pinout/pin37_gpio26/): water level out (echo)

#### Method

- Uses time between the echo and response to deterine the distances.

#### References

- <https://www.google.com/search?q=DYP-A01-V2.0>
- <https://www.dypcn.com/uploads/A02-Datasheet.pdf>

### Momentary Button

`<section incomplete>`

## Design Decisions

### Python Version 3.6 >=

Minimum python version of 3.6 to support `printf()`

### Delays in Reading Temp/Humidity data

Reading sensor values  with inheritly long delays and responding to the REST API. To minimize the delay in subsequent readings the value is cached and given if another read occurs within two seconds.

### GPIO

Using `gpiozero` to leverage `pigpio` daemon which is hardware driven and more efficient.This ensures better accuracy of the distance sensor and is less cpu intesive when using PWMs.

## Rest API

`<section incomplete>`

## File Structure

```
<gardyn-of-eden>
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

## Electrical Diagrams

Incase you need to troubleshoot any problems with your system.

### Sensors

<img src="docs/pcb1.png" width="800px">

### Power and Header

<img src="docs/pcb2.png" width="800px">

## Milestones

- [ ] [Hardware Interface](https://github.com/iot-root/gardyn-of-eden/milestone/6)
  - [x] [pump](https://github.com/iot-root/gardyn-of-eden/issues/33)
  - [x] [lights](https://github.com/iot-root/gardyn-of-eden/issues/34)
  - [x] [temp & humidty](https://github.com/iot-root/gardyn-of-eden/issues/35)
  - [ ] [button](https://github.com/iot-root/gardyn-of-eden/issues/36)
  - [x] [motor current & overtemp](https://github.com/iot-root/gardyn-of-eden/issues/37)
  - [x] [distance/waterlevel](https://github.com/iot-root/gardyn-of-eden/issues/38)
  - [ ] [camera](https://github.com/iot-root/gardyn-of-eden/issues/40)
- [x] [Rest API](https://github.com/iot-root/gardyn-of-eden/milestone/7)
- [ ] [Dashboard](https://github.com/iot-root/gardyn-of-eden/milestone/8)

## TODO

- [ ] test compatibility pi models: pi-zero, pi-zero 2
- [ ] simple scheduling interface...
- [x] Reverse engineer and document hardware, software
  - [x] [Electrical Diagrams](#electrical-diagrams)
- [ ] document API endpoints
- [ ] Figure out temp humidity and onboard motor sensor via i2c
- [ ] Add homeassistant support
- [ ] Rewrite for to collect data for graphs and analytics
- [ ] Dockerize?
- [ ] crontab -e
- [ ] lighting: do more technical research for optimal PWM driving.

## Notes

```
mosquitto_passwd -c /etc/mosquitto/passwd <username>

#/etc/mosquitto/mosquitto.conf

pid_file /run/mosquitto/mosquitto.pid

persistence true
persistence_location /var/lib/mosquitto/

log_dest file /var/log/mosquitto/mosquitto.log

listener 1883 0.0.0.0

allow_anonymous false
password_file /etc/mosquitto/passwd

include_dir /etc/mosquitto/conf.d
```
