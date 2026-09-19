#!/usr/bin/env python3
"""Verifies #131 on real hardware: the light keeps its level when another
process builds a Light, and the button toggles the light's real state.

Needs pigpiod running and the repo venv. The LIGHT WILL CHANGE BRIGHTNESS
during the test (40%, a ramp toward 20%, 50%, 30%, 35%, off). The pump driver is constructed when
mqtt.py is imported, which only ever sets the pump OFF; the pump never runs.
The light is switched off at the end.

    venv/bin/python tests/on_pi/check_light_state.py [--skip-ramp]

Each step reads the pin's duty cycle straight from pigpiod over its own
connection, so it sees what the hardware is doing, not what a process cached.
"""

# hardware: yes

import argparse
import os
import subprocess
import sys
import tempfile
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PY = sys.executable
TOLERANCE = 1.5  # percent

# Keep test state out of ~/.garden_state.json and the log out of the repo.
WORKDIR = tempfile.mkdtemp(prefix="goe-light-check-")
os.environ["STATE_FILE"] = os.path.join(WORKDIR, "state.json")
os.environ.pop("PYTHONPATH", None)
sys.path.insert(0, REPO)

import pigpio  # noqa: E402

import config  # noqa: E402

PIN = config.LIGHT_PIN
results = []


def duty_pct(pi):
    """The light pin's duty cycle in percent, as pigpiod reports it."""
    try:
        return 100.0 * pi.get_PWM_dutycycle(PIN) / pi.get_PWM_range(PIN)
    except pigpio.error:
        return 0.0  # pin not in PWM mode: off


def check(name, ok, detail=""):
    results.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))


def near(actual, expected):
    return abs(actual - expected) <= TOLERANCE


def run(*args, cwd=REPO):
    """Run a helper process the way cron or a restart would, and wait for it.

    PYTHONPATH is set the way bin/light.sh sets it, so this check doesn't
    depend on #129 (covered by check_cli_imports.sh)."""
    env = dict(os.environ, PYTHONPATH=REPO)
    proc = subprocess.run(
        [PY, *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=120
    )
    if proc.returncode != 0:
        print(proc.stdout + proc.stderr)
    return proc


def light_cli(*args):
    return run(os.path.join(REPO, "app", "sensors", "light", "light.py"), *args, cwd="/")


def set_level(pct):
    light_cli("--on", "--brightness", str(pct))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skip-ramp", action="store_true", help="skip the ~20s sunset-ramp check")
    args = parser.parse_args()

    pi = pigpio.pi()
    if not pi.connected:
        sys.exit("pigpiod is not running (sudo systemctl start pigpiod)")

    try:
        print("== creating a Light in another process must not change the level")
        set_level(40)
        level = duty_pct(pi)
        check("light CLI sets 40%", near(level, 40), f"{level:.1f}%")

        light_cli()  # no action: just constructs Light, like any cron/CLI start
        level = duty_pct(pi)
        check("light.py with no action leaves it at 40%", near(level, 40), f"{level:.1f}%")

        # The REST API builds every driver when its blueprints are imported.
        # (Keep the app referenced: a Light that is garbage-collected closes its
        # pin, which switches the light off; that is gpiozero, not a restart.)
        run("-c", "import app; a = app.create_app()")
        level = duty_pct(pi)
        check("starting the REST app leaves it at 40%", near(level, 40), f"{level:.1f}%")

        if not args.skip_ramp:
            print("== sunset ramp starts from the current level")
            set_level(40)
            ramp = subprocess.Popen(
                [PY, "app/sensors/light/light.py", "--brightness", "20", "--ramp-minutes", "1"],
                cwd=REPO,
                env=dict(os.environ, PYTHONPATH=REPO),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            samples = []
            deadline = time.time() + 20
            while time.time() < deadline:
                samples.append(duty_pct(pi))
                time.sleep(0.2)
            ramp.terminate()
            ramp.wait(timeout=10)
            # Skip the first samples: the process is still importing and the
            # light is untouched. Once it runs, it must never drop toward 0.
            active = [s for s in samples if not near(s, 40)] or samples[-1:]
            check(
                "ramp 40% -> 20% fades down instead of snapping to 0",
                min(active) >= 30 and samples[-1] < 40,
                f"min {min(samples):.1f}%, last {samples[-1]:.1f}%",
            )

        print("== button single press toggles the real state (mqtt.py)")
        set_level(40)
        os.chdir(WORKDIR)  # mqtt.py writes mqtt.log to the working directory
        import mqtt

        class FakeClient:
            def __init__(self):
                self.published = []

            def publish(self, topic, payload=None, *a, **kw):
                self.published.append((topic, payload))

        mqtt.client = FakeClient()
        level = duty_pct(pi)
        check(
            "importing mqtt.py (service start) leaves it at 40%", near(level, 40), f"{level:.1f}%"
        )

        # The service believes the light is off, as it does when HA, the API or
        # a schedule turned it on.
        mqtt.light_state = False
        mqtt.handle_single_press()
        level = duty_pct(pi)
        check("press while on (set elsewhere) turns it off", near(level, 0), f"{level:.1f}%")

        mqtt.handle_single_press()
        level = duty_pct(pi)
        check(
            f"next press turns it on at {mqtt.brightness}%",
            near(level, mqtt.brightness),
            f"{level:.1f}%",
        )

        set_level(30)  # another process changes it while the service runs
        mqtt.handle_single_press()
        level = duty_pct(pi)
        check("press after another process set 30% turns it off", near(level, 0), f"{level:.1f}%")

        print("== Home Assistant light commands persist state")
        from app.lib import state as state_lib

        class Msg:
            def __init__(self, suffix, payload):
                self.topic = f"{mqtt.BASE_TOPIC}/{suffix}"
                self.payload = payload.encode()

        mqtt.on_message(mqtt.client, None, Msg("light/command", "ON"))
        saved = state_lib.load_state()
        level = duty_pct(pi)
        check(
            "HA ON: light on and saved",
            level > 0 and saved.get("light_on") is True,
            f"{level:.1f}%, {saved}",
        )

        mqtt.on_message(mqtt.client, None, Msg("light/brightness/set", "35"))
        saved = state_lib.load_state()
        level = duty_pct(pi)
        check(
            "HA brightness 35: level and saved brightness",
            near(level, 35) and saved.get("brightness") == 35 and saved.get("light_on") is True,
            f"{level:.1f}%, {saved}",
        )

        mqtt.on_message(mqtt.client, None, Msg("light/command", "OFF"))
        saved = state_lib.load_state()
        level = duty_pct(pi)
        check(
            "HA OFF: light off and saved",
            near(level, 0) and saved.get("light_on") is False,
            f"{level:.1f}%, {saved}",
        )
    finally:
        light_cli("--off")
        print(f"\n  light switched off (now {duty_pct(pi):.1f}%)")
        pi.stop()

    passed = sum(results)
    print(f"\ncheck_light_state: {passed} passed, {len(results) - passed} failed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    code = main()
    sys.stdout.flush()
    # Skip gpiozero's exit cleanup: mqtt.py's distance sensor thread would
    # otherwise race the closed pigpio connection and print a traceback.
    os._exit(code)
