"""Grow-cycle tracking and time-based reminders.

Covers the grow-cycle notification issues: thinning (#6), root check (#5),
harvest/trim (#62), and nutrient/"food" reminders (#4). A cycle has a start
date; reminders become "due" once enough days have elapsed since the start.

Pure logic with an injectable ``now`` so it can be unit-tested deterministically.
The MQTT service persists/loads state via load_state/save_state and publishes
due reminders.
"""

import json
from datetime import datetime

import config
from app.lib.persist import write_json_atomic

STAGES = ["germination", "thinning", "root_check", "harvest"]


def default_state(now=None):
    now = now or datetime.now()
    return {"stage": "germination", "started": now.isoformat(), "acknowledged": []}


def load_state():
    try:
        with open(config.GROW_STATE_FILE) as fh:
            return json.load(fh)
    except (FileNotFoundError, ValueError):
        return default_state()


def save_state(state):
    write_json_atomic(config.GROW_STATE_FILE, state)


def start_cycle(now=None):
    """Begin a fresh grow cycle (resets stage, start date, acknowledgements)."""
    state = default_state(now)
    save_state(state)
    return state


def _days_since(started_iso, now):
    try:
        started = datetime.fromisoformat(started_iso)
    except (TypeError, ValueError):
        return 0
    return (now - started).days


def due_reminders(state, now=None):
    """Return reminder keys that are due and not yet acknowledged.

    One-shot grow-stage reminders fire once their day threshold passes; the
    recurring nutrient reminder fires every NUTRIENT_REMINDER_DAYS.
    """
    now = now or datetime.now()
    days = _days_since(state.get("started"), now)
    acked = set(state.get("acknowledged", []))
    due = []

    one_shot = {
        "thinning": config.THINNING_REMINDER_DAYS,
        "root_check": config.ROOT_CHECK_REMINDER_DAYS,
        "harvest": config.HARVEST_REMINDER_DAYS,
    }
    for key, threshold in one_shot.items():
        if threshold and days >= threshold and key not in acked:
            due.append(key)

    cadence = config.NUTRIENT_REMINDER_DAYS
    if cadence and days > 0 and days % cadence == 0 and f"nutrient_day{days}" not in acked:
        due.append("nutrient")

    return due


def acknowledge(state, key, now=None):
    """Mark a reminder handled so it stops firing.

    The recurring nutrient reminder is acked per-day so it can fire again next
    cadence window.
    """
    now = now or datetime.now()
    acked = set(state.get("acknowledged", []))
    if key == "nutrient":
        days = _days_since(state.get("started"), now)
        acked.add(f"nutrient_day{days}")
    else:
        acked.add(key)
    state["acknowledged"] = sorted(acked)
    return state


def set_stage(state, stage):
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage!r}; expected one of {STAGES}")
    state["stage"] = stage
    return state
