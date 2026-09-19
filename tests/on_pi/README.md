# On-Pi verification scripts

Checks that a fix works on a real unit. They are not unit tests: CI doesn't run
them (`unittest discover` only collects `test_*.py`), and some of them drive the
hardware.

```bash
cd ~/garden-of-eden
sudo systemctl start pigpiod
tests/on_pi/run_all.sh            # every check_* script here
tests/on_pi/run_all.sh --no-hw    # skip the ones that drive pins
```

Stop `mqtt.service` and `garden-api.service` first if they are installed, so
they don't change the light or pump under the test.

## Adding a check

Name it `check_<topic>.sh` or `check_<topic>.py`; `run_all.sh` picks it up
automatically. Start it with a comment saying which issue it verifies and what
it touches, and print one `PASS`/`FAIL` line per assertion plus a
`<name>: N passed, M failed` summary. Exit non-zero if anything failed.

If it drives the hardware (changes the light, runs the pump), say so in the
header and add this line so `--no-hw` can skip it:

```
# hardware: yes
```

A good check is run against the unfixed code first, on the unit, to prove it
reproduces the problem the issue describes.
