# Accessing the unit after flashing

## 1. Flash with SSH + networking enabled (first access)

You need SSH to run `bin/setup.sh` the first time, so enable it when you flash
the card. In the **Raspberry Pi Imager**, click the ⚙ (advanced options) and set:

- **Enable SSH** (password or public-key)
- **Username / password** (e.g. user `gardyn`)
- **Hostname**: `gardyn`
- **Wi‑Fi** SSID + password + country

> Headless alternative (no Imager UI): after flashing, on the boot partition
> create an empty file named `ssh`, plus a `userconf.txt` and `wpa_supplicant.conf`.
> See the Raspberry Pi headless setup docs.

Then boot the Pi and connect:

```bash
ssh gardyn@gardyn.local
```

## 2. Install — SSH stays on, mDNS is added

`bin/setup.sh` keeps SSH enabled and installs `avahi-daemon` + sets the hostname,
so the unit is reliably reachable at **`gardyn.local`** afterward (override with
`GARDEN_HOSTNAME=… ./bin/setup.sh`). It also installs **`garden-api.service`**,
which serves the web UI/REST API on boot.

```bash
git clone https://github.com/iot-root/garden-of-eden.git
cd garden-of-eden
cp .env-dist .env && nano .env

./bin/setup.sh --dry-run   # preview every system change; makes NO changes
./bin/setup.sh             # prompts for confirmation before applying
```

### Safety

`setup.sh` is designed not to brick the device:

- **`--dry-run`** prints every `sudo` change and exits without touching anything.
- It **prompts for confirmation** before applying (skip with `--yes`).
- Every system file it edits (`config.txt`, `/etc/modules`, `/etc/hosts`) is
  **backed up** to `<file>.garden.bak` first.
- It detects the correct boot config path (`/boot/firmware/config.txt` on
  Bookworm, `/boot/config.txt` on older releases).
- **`bin/uninstall.sh`** reverses the install: stops/removes the services,
  removes symlinks/udev rules and our cron entries, and restores the backups.
  (It leaves apt packages, group membership, and SSH enabled — harmless.)

If a boot/I2C change ever causes trouble, pop the SD card into any computer and
restore `config.txt` from `config.txt.garden.bak` on the boot partition.

## 3. Use it

- **Web UI:** http://gardyn.local:5000/
- **REST API:** same host, e.g. `curl http://gardyn.local:5000/system`
- **SSH:** `ssh gardyn@gardyn.local`
- **Home Assistant:** auto-discovers over MQTT (see the README).

If `gardyn.local` doesn't resolve (some Android/Windows setups), use the Pi's IP
(`hostname -I` over SSH, or check your router). To lock down the API over the
network, set `GARDEN_API_KEY` in `.env` and enter it in the web UI's ⚙ settings.

## Public HTTPS access with Cloudflare Tunnel

The Compose file includes an opt-in `cloudflared` service. It creates an
outbound tunnel, so the router does not need port forwarding and port 5000 does
not need to be exposed publicly. Cloudflare provides HTTPS for the hostname.

Before starting it:

1. Create a Cloudflare Tunnel and configure its public hostname to forward to
  `http://host.docker.internal:5000`.
2. Copy the tunnel token into the Pi-local `.env` as
  `CLOUDFLARE_TUNNEL_TOKEN=...`. Never commit the token.
3. Generate a long random `GARDEN_API_KEY` and set it in the same `.env`.
4. Start the public profile:

```bash
docker compose --profile public up -d cloudflared
```

Open the Cloudflare hostname over HTTPS and enter the API key in the web UI
settings. The UI shell and `/health` remain public, while sensor and actuator
endpoints require `X-API-Key`.

Check and stop the tunnel with:

```bash
docker compose logs -f cloudflared
docker compose --profile public stop cloudflared
```

Treat the Cloudflare token and API key as credentials. The tunnel is optional;
the local systemd service remains the normal Pi deployment path.

## Private HTTPS access with Tailscale

Tailscale is the recommended no-domain option for private remote access. It
creates an encrypted tailnet connection and exposes the local Garden of Eden API
over HTTPS without opening a router port.

On the Pi, enable Serve for the systemd API:

```bash
sudo tailscale serve --bg http://127.0.0.1:5000
tailscale serve status
```

Install Tailscale and sign in with the same account on the phone or computer
that will view the UI. Open the HTTPS URL printed by `tailscale serve status`.
It normally has this form:

```text
https://<device>.<tailnet>.ts.net/
```

This address is tailnet-only. Stop the proxy with:

```bash
sudo tailscale serve --https=443 off
```

The generated Tailscale hostname is account/device configuration and should not
be hard-coded into the repository.

## Services

```bash
sudo systemctl status garden-api.service   # web UI + REST
sudo systemctl status mqtt.service         # MQTT / Home Assistant
sudo systemctl status ssh                  # remote access
```
