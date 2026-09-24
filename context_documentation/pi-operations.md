# Pi Operations

The repository's operational scripts are intended to run on the Raspberry Pi, not from the development workstation.

## Configure local SSH values

Do not commit a personal username, local IP address, hostname, password, private key, or API key. Set the connection values only in the operator's local shell configuration:

```bash
cat >> ~/.bashrc <<'EOF'
export GARDEN_PI_USER="your-pi-user"
export GARDEN_PI_HOST="your-pi-host-or-ip"
EOF
source ~/.bashrc
```

Replace the placeholder values locally. The resulting connection is equivalent to:

```bash
ssh "${GARDEN_PI_USER}@${GARDEN_PI_HOST}"
```

For a one-off session, export the variables directly in the shell instead of editing `~/.bashrc`.

## Mount the Pi checkout in WSL

The Pi checkout can be mounted into the local workspace with SSHFS so VS Code can inspect and edit the remote repository:

```bash
cd /tmp
/home/<local-user>/scripts/pi-mount mount
```

The script in `~/scripts/pi-mount` installs the actual helper at `/usr/local/bin/pi-mount`. After installation, use the helper directly:

```bash
/usr/local/bin/pi-mount status
/usr/local/bin/pi-mount mount
```

The mount target is `/home/<local-user>/pi` and the remote checkout is `/home/<pi-user>/garden-of-eden`. Mount SSHFS as the normal local user, not with `sudo sshfs`, so the mounted files remain readable and writable by VS Code. Run the mount command from a healthy directory such as `/tmp` if the previous mount became disconnected.

Unmount it with:

```bash
/usr/local/bin/pi-mount unmount
```

## Run repository scripts

Connect to the Pi and run commands from the checkout there:

```bash
ssh "${GARDEN_PI_USER}@${GARDEN_PI_HOST}"
cd ~/garden-of-eden
./bin/get-sensor-data.sh
./bin/water.sh
./bin/light.sh
```

Use the script's `--help` output or its source for command-specific options. Check `docs/INSTALL.md` and `docs/maintenance.md` before changing services or hardware configuration.

## Run all tests on the Pi

Run the test suite from the Pi checkout using the development environment:

```bash
ssh "${GARDEN_PI_USER}@${GARDEN_PI_HOST}" \
	'cd ~/garden-of-eden && .venv-dev/bin/python -m pytest'
```

Create the environment and install the development dependencies once if `.venv-dev` does not exist:

```bash
ssh "${GARDEN_PI_USER}@${GARDEN_PI_HOST}" \
	'cd ~/garden-of-eden && python3 -m venv .venv-dev && .venv-dev/bin/pip install -r requirements-dev.txt'
```

For a focused run, append a test path or expression, for example:

```bash
ssh "${GARDEN_PI_USER}@${GARDEN_PI_HOST}" \
	'cd ~/garden-of-eden && .venv-dev/bin/python -m pytest tests/test_api.py'
```

The suite uses hardware stubs and the simulator, so passing tests do not replace live checks of GPIO, I2C sensors, cameras, pigpiod, systemd, or MQTT discovery on the connected hardware.

## Run the web UI as a service

The Pi web UI is served by Waitress through `garden-api.service`, using the repository runtime environment:

```text
/home/<pi-user>/garden-of-eden/venv/bin/waitress-serve
```

Check the service and recent logs with:

```bash
sudo systemctl status garden-api.service
sudo journalctl -u garden-api.service -n 40 --no-pager
```

The UI is available at `http://${GARDEN_PI_HOST}:5000/`, and the health endpoint is `/health`. Use the private `GARDEN_PI_HOST` value from the local shell environment rather than recording a device address here.

The API can still start when `.env` is absent because configuration defaults are available, but sensor endpoints may report unavailable hardware. In particular, verify I2C configuration and sensor wiring when the service logs report that no hardware I2C bus is available.

For a Pi model with only an upper camera, set this in the Pi-local `.env`:

```env
LOWER_CAMERA_ENABLED=false
```

The API then reports one camera, the lower-camera route returns `404`, MQTT skips lower-camera discovery and publishing, and the web UI hides the lower-camera controls. The default remains enabled for two-camera models.

## Safety notes

- Confirm the current host before running pump, light, water, update, or uninstall scripts.
- Keep `.env` and other credentials on the Pi or in an ignored local file.
- Review a script before running it with elevated privileges.
- The Pi may use mDNS (`gardyn.local`) when available, but the environment variables above are the canonical private connection settings for this workspace.
