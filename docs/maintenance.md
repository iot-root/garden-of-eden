# Maintenance & Self-Repair (issue #64)

## Updating

```bash
garden-update          # symlinked to bin/update.sh by setup.sh
# or: ./bin/update.sh
```

This pulls the latest code, refreshes the venv, and restarts `mqtt.service`.

## Checking service health

```bash
sudo systemctl status pigpiod
sudo systemctl status mqtt.service
sudo systemctl status mosquitto      # if the broker runs on the Pi
./bin/show-mqtt-logs.sh              # journalctl -u mqtt.service
tail -f gardyn.log                   # application log (LOG_FILE)
```

## Verifying hardware

```bash
sudo i2cdetect -y 1                  # expect 0x48 (PCB temp), 0x40 (INA219),
                                     # 0x38 (DHT20) or 0x5c (AM2320)
curl localhost:5000/system           # detected model + sensor profile
curl localhost:5000/temperature      # 503 means the sensor is unreachable
./bin/api-test.sh                    # exercise every REST endpoint
```

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `Failed to connect to pigpiod` | daemon not running | `sudo systemctl start pigpiod` |
| Sensor endpoint returns 503 | I2C device unplugged / wrong `SENSOR_TYPE` | reseat; check `i2cdetect`; set `SENSOR_TYPE` |
| Light flickers | software PWM / wrong factory | ensure pigpio is used (it is by default) |
| Camera 503 | `fswebcam` missing or wrong device | `sudo apt install fswebcam`; check `UPPER_CAMERA_DEVICE` |
| Cameras swap after reboot | unstable `/dev/videoN` | install udev rules (`bin/setup.sh`), use `/dev/gardyn-*` |
| Water-low never triggers | `WATER_LOW_CM` unset/0 | set a threshold in `.env` |

## Resetting state

Actuator/grow/schedule state is stored in your home dir:

```bash
rm ~/.garden_state.json ~/.garden_grow.json ~/.garden_schedule.json
```

(Paths are configurable via `STATE_FILE`, `GROW_STATE_FILE`, `SCHEDULE_FILE`.)
