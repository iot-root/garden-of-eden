# Installing on a Raspberry Pi

These notes are for whoever is doing the install on the actual Gardyn Pi.
Follow them top to bottom. The install is
designed to be brick-safe (dry-run, backups, uninstall) — see "Safety" below.

> Check out the branch you intend to run before starting (`git branch --show-current`).

---

## 0. Prerequisites (flashing)

Flash Raspberry Pi OS (Lite is fine) with the **Raspberry Pi Imager**. In the
⚙ advanced options set:

- **Enable SSH** (you need it to run the installer)
- **Username/password** (e.g. user `gardyn`)
- **Hostname** `gardyn`
- **Wi-Fi** SSID + password + country

Boot the Pi, then SSH in:

```bash
ssh gardyn@gardyn.local      # or use the Pi's IP if .local doesn't resolve
```

## 1. Get the code (the right branch)

```bash
git clone https://github.com/HeatherFlux/garden-of-eden.git
cd garden-of-eden
git checkout main   # or the branch you intend to run
```

## 2. Configure

```bash
cp .env-dist .env
nano .env
```

Set at least:
- `MQTT_USERNAME` / `MQTT_PASSWORD` (your mosquitto creds)
- `MQTT_IDENTIFIER` (unique per unit, e.g. `gardyn_03`)
- `WATER_LOW_CM` (low-water threshold; `0` disables)
- Optionally `GARDEN_API_KEY` to require a key for remote API access.

`SENSOR_TYPE` is **auto-detected** by setup (AM2320 vs DHT20) — leave it unset.

## 3. Install (safe)

```bash
./bin/setup.sh --dry-run     # preview every system change; makes NO changes
./bin/setup.sh               # asks for confirmation before applying
```

What it does: apt deps, a Python venv, enables I2C, adds you to `i2c/gpio/dialout`
groups, installs the `light`/`water`/`garden-update` CLIs, camera udev rules,
enables SSH + mDNS, and installs/starts the `mqtt.service` and `garden-api.service`
systemd units. Takes a few minutes (apt + pip).

## 4. Reboot

I2C and new group membership need a reboot to take effect:

```bash
sudo reboot
```

## 5. Verify

```bash
sudo systemctl status pigpiod mqtt.service garden-api.service   # all active
sudo i2cdetect -y 1                                             # expect 0x40,0x48, and 0x38 or 0x5c
curl localhost:5000/health                                      # {"status":"ok"}
curl localhost:5000/system                                      # model/version
curl localhost:5000/temperature                                 # a number (503 = sensor unreachable)
./bin/api-test.sh                                               # exercises all endpoints
```

Then open the web UI from any device on the network: **http://gardyn.local:5000/**

### Hardware sanity (do gently)
- Toggle the **light** first (lowest risk).
- For the **pump**, use a short run (e.g. `water 5`) and watch it — make sure it
  actually moves water and stops. Don't run the pump dry.

## 6. Home Assistant (optional)

Have an MQTT broker (mosquitto on the Pi or on HA). With `.env` MQTT creds set and
`mqtt.service` running, the device **auto-discovers** in HA with all entities
(light, pump, temp, humidity, PCB temp, water level + low alert, cameras, button).
Dashboard example: `docs/homeassistant/lovelace-example.yaml`.

## Safety / recovery

- `setup.sh --dry-run` shows everything first and changes nothing.
- Every system file edited (`config.txt`, `/etc/modules`, `/etc/hosts`) is backed
  up to `<file>.garden.bak`.
- **Undo the install:** `./bin/uninstall.sh` (stops/removes services, restores
  backups, removes our cron entries; leaves apt packages + SSH alone).
- **Won't boot after an I2C change?** Put the SD card in any computer and copy
  `config.txt.garden.bak` over `config.txt` on the boot partition. No reflash.
- Logs: `journalctl -u garden-api.service`, `journalctl -u mqtt.service`, and
  `gardyn.log` in the repo dir.

## Updating later

```bash
garden-update        # = bin/update.sh: git pull + pip install + restart services
```

A nightly timer (`garden-autoupdate.timer`, ~03:30) does the same pull automatically
and restarts the services only when the branch actually moved; it fast-forwards only,
so it never discards local changes. Disable it with
`sudo systemctl disable --now garden-autoupdate.timer` if you'd rather update by hand.

```bash
```

---

## Notes for the install

- **Always run `./bin/setup.sh --dry-run` first** and read the plan before running
  the real install. `--yes` skips the confirmation prompt.
- The **simulator** (`python -m simulator.serve` / `mqtt_sim`) is for *off-Pi*
  testing only — do **not** run it on the Pi; the real services serve the app.
- Expect a **reboot** between install and verification.
- Off-Pi-only quirks don't apply here: on the Pi, `fswebcam` (cameras) and real
  I2C sensors exist, so `/camera/*` and sensor endpoints should return real data.
- Raspberry Pi OS Bookworm keeps boot config at `/boot/firmware/config.txt`;
  setup detects this automatically — don't hand-edit the wrong path.
- If a service is failing, check `journalctl -u <svc>` before changing anything;
  most issues are a missing `.env` value or pigpiod not running.
