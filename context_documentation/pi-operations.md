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

## Run the test suite

Prefer running the suite **off the Pi**, on the development workstation or with the simulator. The stubs in `tests/_hwstub.py` install themselves only when the Blinka `board` package is *not* importable. On the Pi it is importable, so `install()` returns early and **no stubs are installed at all** — the suite then constructs real `Light`/`Pump` objects, opens real pigpiod connections, and reads real I2C devices. Treat a test run on the Pi as a live hardware exercise, not a unit test run.

From a checkout with `.venv-dev` (see `README.md`), run:

```bash
.venv-dev/bin/python -m pytest
.venv-dev/bin/ruff check .
.venv-dev/bin/black --check .
```

`requirements-dev.txt` deliberately lists only pure-Python packages, so a development environment created from it has no `board` and the stubs install normally. Never run the suite with the runtime `venv` on the Pi.

If a focused check must run on the Pi, prefer a module that does not touch GPIO or I2C, and confirm the hardware is in a safe state first:

```bash
ssh "${GARDEN_PI_USER}@${GARDEN_PI_HOST}" \
	'cd ~/garden-of-eden && .venv-dev/bin/python -m pytest tests/test_models.py'
```

Regardless of where it runs, a passing suite does not replace live acceptance checks of GPIO, I2C sensors, cameras, pigpiod, systemd, and MQTT discovery on the connected hardware.

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

The camera count follows the detected model: a Gardyn 3.0 or Studio reports one
camera, the lower-camera route returns `404`, MQTT skips lower-camera discovery
and publishing, and the web UI hides the lower-camera controls. Models with both
cameras (1.0/2.0) report two. For a unit that differs from its profile,
override it in the Pi-local `.env`:

```env
LOWER_CAMERA_ENABLED=false
```

## Private HTTPS with Tailscale

Tailscale Serve proxies the private HTTPS endpoint to the local API on port 5000.
This does not require a purchased domain, router port forwarding, or a public
internet listener.

Install and sign in to Tailscale on each client device, then open the device
hostname shown by `tailscale serve status`:

```bash
sudo tailscale serve --bg http://127.0.0.1:5000
tailscale serve status
```

The URL has the form `https://<device>.<tailnet>.ts.net/` and is available only
to devices signed in to the same tailnet. Disable the proxy with:

```bash
sudo tailscale serve --https=443 off
```

Keep generated Tailscale hostnames and tailnet names in local configuration or
the Tailscale admin console, not in committed repository files.

## Safety notes

- Confirm the current host before running pump, light, water, update, or uninstall scripts.
- Keep `.env` and other credentials on the Pi or in an ignored local file.
- Review a script before running it with elevated privileges.
- The Pi may use mDNS (`gardyn.local`) when available, but the environment variables above are the canonical private connection settings for this workspace.
