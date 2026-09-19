"""Lights/pump scheduling that survives reboots and PC shutdown by writing the
Pi's crontab (issue #32).

The schedule is persisted as JSON and compiled into crontab lines tagged with a
marker comment so we can rewrite only our own entries. Cron invokes the
``light`` and ``water`` CLI symlinks installed by bin/setup.sh.

Each of ``lights`` and ``pump`` holds a ``days`` map keyed by weekday
(``mon``..``sun``); every weekday carries a list of entries, so you can set as
many light windows and pump runs per day as you like:

    {
      "lights": {"enabled": true, "days": {
        "mon": [{"onTime": "06:00", "offTime": "22:00", "brightness": 70}], ...
      }},
      "pump": {"enabled": true, "days": {
        "mon": [{"time": "08:00", "duration": 5}, {"time": "16:00", "duration": 5}], ...
      }}
    }

Older single-window schedules (``lights.onTime`` / ``pump.runs``) are migrated
to this shape on load, so existing saved schedules and clients keep working.
"""

import datetime
import json
import logging
import os
import subprocess

import config
from app.lib.persist import write_json_atomic

logger = logging.getLogger(__name__)

CRON_MARKER = "# garden-of-eden"
LIGHT_CMD = "/usr/local/bin/light"
WATER_CMD = "/usr/local/bin/water"

# schedule-refresh CLI (absolute path): run nightly so vacation mode auto-expires.
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
REFRESH_CMD = os.path.join(_REPO_ROOT, "bin", "schedule-refresh.sh")

# Reduced light/water applied to every day while Vacation mode is active.
VACATION_PROFILE = {
    "lights": [{"onTime": "10:00", "offTime": "16:00", "brightness": 50}],
    "pump": [{"time": "12:00", "duration": 3}],
}

# Weekday order and the cron day-of-week number each maps to (cron: Sun=0).
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_TO_CRON = {"mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6, "sun": 0}

DEFAULT_SCHEDULE = {
    "lights": {"enabled": False, "days": {d: [] for d in DAYS}},
    "pump": {"enabled": False, "days": {d: [] for d in DAYS}},
    "vacation": {"enabled": False, "until": None},
}


def _empty_days():
    return {d: [] for d in DAYS}


def normalize_schedule(schedule):
    """Coerce any accepted schedule shape into the canonical per-day form.

    Accepts the current ``days`` layout, the legacy single-window layout
    (``lights.onTime``/``offTime``/``brightness`` and ``pump.runs``), or a mix,
    and always returns a dict with full ``mon``..``sun`` day maps.
    """
    schedule = schedule or {}
    lights = dict(schedule.get("lights") or {})
    pump = dict(schedule.get("pump") or {})

    # --- lights ---
    light_days = _empty_days()
    if isinstance(lights.get("days"), dict):
        for day, entries in lights["days"].items():
            if day in light_days and isinstance(entries, list):
                light_days[day] = [dict(e) for e in entries]
    elif lights.get("onTime") or lights.get("offTime"):
        # Legacy: one window applied to every day.
        window = {
            "onTime": lights.get("onTime", "08:00"),
            "offTime": lights.get("offTime", "22:00"),
            "brightness": int(lights.get("brightness", 70)),
        }
        light_days = {d: [dict(window)] for d in DAYS}

    # --- pump ---
    pump_days = _empty_days()
    if isinstance(pump.get("days"), dict):
        for day, entries in pump["days"].items():
            if day in pump_days and isinstance(entries, list):
                pump_days[day] = [dict(e) for e in entries]
    elif isinstance(pump.get("runs"), list):
        # Legacy: same set of runs applied to every day.
        runs = [dict(r) for r in pump["runs"]]
        pump_days = {d: [dict(r) for r in runs] for d in DAYS}

    vacation = dict(schedule.get("vacation") or {})

    return {
        "lights": {"enabled": bool(lights.get("enabled")), "days": light_days},
        "pump": {"enabled": bool(pump.get("enabled")), "days": pump_days},
        "vacation": {
            "enabled": bool(vacation.get("enabled")),
            "until": vacation.get("until") or None,
        },
    }


def load_schedule():
    """Return the saved schedule (normalized), or defaults if none exists."""
    try:
        with open(config.SCHEDULE_FILE) as fh:
            return normalize_schedule(json.load(fh))
    except (FileNotFoundError, ValueError):
        return normalize_schedule(DEFAULT_SCHEDULE)


def save_schedule(schedule):
    write_json_atomic(config.SCHEDULE_FILE, schedule)


def _hh_mm(value):
    """Parse "HH:MM" -> (minute, hour) for cron, or raise ValueError."""
    hour, minute = value.split(":")
    h, m = int(hour), int(minute)
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(f"invalid time {value!r}")
    return m, h


def _pump_seconds(duration_minutes):
    """Minutes -> seconds, clamped to the hard safety cap (config.MAX_PUMP_RUN_SECONDS)."""
    seconds = int(duration_minutes) * 60
    if seconds < 1:
        raise ValueError(f"invalid pump duration {duration_minutes!r}")
    return min(seconds, config.MAX_PUMP_RUN_SECONDS)


def is_vacation_active(schedule, today=None):
    """True when Vacation mode is on and not past its end date (``until``)."""
    vacation = schedule.get("vacation") or {}
    if not vacation.get("enabled"):
        return False
    until = vacation.get("until")
    if not until:
        return True  # no end date -> active until manually turned off
    today = today or datetime.date.today()
    try:
        return today <= datetime.date.fromisoformat(until)
    except ValueError:
        return True


def _vacation_cron_lines():
    """Minimal keep-alive light/water for every day, plus a nightly refresh so
    vacation mode reverts to the normal schedule once its end date passes."""
    lines = []
    for day in DAYS:
        dow = DAY_TO_CRON[day]
        for window in VACATION_PROFILE["lights"]:
            on_m, on_h = _hh_mm(window["onTime"])
            off_m, off_h = _hh_mm(window["offTime"])
            brightness = int(window["brightness"])
            lines.append(f"{on_m} {on_h} * * {dow} {LIGHT_CMD} {brightness} {CRON_MARKER}")
            lines.append(f"{off_m} {off_h} * * {dow} {LIGHT_CMD} off {CRON_MARKER}")
        for run in VACATION_PROFILE["pump"]:
            run_m, run_h = _hh_mm(run["time"])
            seconds = _pump_seconds(run["duration"])
            lines.append(f"{run_m} {run_h} * * {dow} {WATER_CMD} {seconds} {CRON_MARKER}")
    lines.append(f"2 0 * * * {REFRESH_CMD} {CRON_MARKER}")
    return lines


def build_cron_lines(schedule):
    """Compile a (normalized) schedule dict into a list of marked crontab lines."""
    schedule = normalize_schedule(schedule)

    # Vacation mode overrides the normal schedule with a reduced keep-alive one.
    if is_vacation_active(schedule):
        return _vacation_cron_lines()

    lines = []

    lights = schedule["lights"]
    if lights["enabled"]:
        for day in DAYS:
            dow = DAY_TO_CRON[day]
            for window in lights["days"][day]:
                brightness = int(window.get("brightness", 70))
                ramp = int(window.get("rampMinutes", 0) or 0)
                on_m, on_h = _hh_mm(window.get("onTime", "08:00"))
                off_m, off_h = _hh_mm(window.get("offTime", "22:00"))
                # light.sh takes positional args: `light <brightness|off>`, or
                # `light ramp <brightness> <minutes>` for a sunrise/sunset fade.
                if ramp > 0:
                    on_cmd = f"{LIGHT_CMD} ramp {brightness} {ramp}"
                    off_cmd = f"{LIGHT_CMD} ramp 0 {ramp}"
                else:
                    on_cmd = f"{LIGHT_CMD} {brightness}"
                    off_cmd = f"{LIGHT_CMD} off"
                lines.append(f"{on_m} {on_h} * * {dow} {on_cmd} {CRON_MARKER}")
                lines.append(f"{off_m} {off_h} * * {dow} {off_cmd} {CRON_MARKER}")

    pump = schedule["pump"]
    if pump["enabled"]:
        for day in DAYS:
            dow = DAY_TO_CRON[day]
            for run in pump["days"][day]:
                run_m, run_h = _hh_mm(run.get("time", "12:00"))
                seconds = _pump_seconds(run.get("duration", 5))
                lines.append(f"{run_m} {run_h} * * {dow} {WATER_CMD} {seconds} {CRON_MARKER}")

    return lines


def _read_crontab():
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()


def _write_crontab(lines):
    payload = "\n".join(lines) + "\n"
    subprocess.run(["crontab", "-"], input=payload, text=True, check=True)


def apply_schedule(schedule):
    """Persist the schedule and replace our crontab entries with its compiled form."""
    # Validate/compile first so a bad schedule never touches crontab.
    schedule = normalize_schedule(schedule)
    cron_lines = build_cron_lines(schedule)
    save_schedule(schedule)

    existing = [ln for ln in _read_crontab() if CRON_MARKER not in ln]
    _write_crontab(existing + cron_lines)
    logger.info("Applied schedule with %d cron entries", len(cron_lines))
    return schedule


def refresh():
    """Re-apply the saved schedule, turning Vacation mode off once its end date
    has passed. Run nightly via cron so vacation auto-expires to the normal
    schedule."""
    schedule = load_schedule()
    vacation = schedule.get("vacation") or {}
    if vacation.get("enabled") and not is_vacation_active(schedule):
        vacation["enabled"] = False
        schedule["vacation"] = vacation
        logger.info("Vacation mode expired; reverting to the normal schedule")
    return apply_schedule(schedule)
