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

## Safety notes

- Confirm the current host before running pump, light, water, update, or uninstall scripts.
- Keep `.env` and other credentials on the Pi or in an ignored local file.
- Review a script before running it with elevated privileges.
- The Pi may use mDNS (`gardyn.local`) when available, but the environment variables above are the canonical private connection settings for this workspace.
