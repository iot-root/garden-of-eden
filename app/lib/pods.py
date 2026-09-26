"""Per-pod plant tracking: each pod has a name and a short 'shape code' (a
sequence of geometric symbols) that mirrors the glyphs printed on the physical
Gardyn pod, so you can match a row in the UI to a pod in the tower.

State is a list of POD_COUNT pods persisted as JSON. Unknown shapes and overlong
names/codes are dropped on normalize so the file can't drift out of spec.
"""

import json
import os

import config
from app.lib import hardware
from app.lib.persist import write_json_atomic

_CATALOG_PATH = os.path.join(os.path.dirname(__file__), "plants.json")

# Allowed symbol keys; the UI renders each as a geometric glyph.
SHAPES = ["circle", "square", "triangle", "diamond", "star", "hexagon", "heart", "plus"]
MAX_SYMBOLS = 5
MAX_NAME = 40


def default_pods():
    return [{"id": i + 1, "name": "", "symbols": []} for i in range(hardware.pod_capacity())]


def load_catalog():
    """The plant variety catalog (name/category/light/difficulty/guide) used to
    populate the UI's variety picker. Returns [] if the data file is missing."""
    try:
        with open(_CATALOG_PATH) as fh:
            return json.load(fh)
    except (FileNotFoundError, ValueError):
        return []


def _clean(pod):
    name = str(pod.get("name", ""))[:MAX_NAME]
    symbols = [s for s in (pod.get("symbols") or []) if s in SHAPES][:MAX_SYMBOLS]
    return name, symbols


def normalize(data):
    """Return exactly one pod per plant port, merging any saved entries by id.

    The count comes from ``hardware.pod_capacity()``, so it follows the
    detected model unless ``POD_COUNT`` overrides it. Only durable state lives
    here (id, name, symbols). Physical position is derived, not stored, so it
    can never go stale when the layout config changes -- see
    :func:`with_positions`.
    """
    by_id = {}
    if isinstance(data, list):
        for pod in data:
            try:
                by_id[int(pod.get("id"))] = pod
            except (TypeError, ValueError):
                continue
    pods = []
    for i in range(hardware.pod_capacity()):
        pid = i + 1
        name, symbols = _clean(by_id.get(pid, {}))
        pods.append({"id": pid, "name": name, "symbols": symbols})
    return pods


def position_for(pod_id):
    """Where a pod sits in the tower, derived from its id.

    ``column`` is 1-based and counted left to right; pods fill down a column
    before moving to the next. ``level`` is 1-based *from the top*, because
    that is the axis that matters: the grow light is at the top of the tower,
    so level 1 is the brightest pod and the highest level is the dimmest.
    ``side`` is the side the pod sticks out on, or None when the unit has no
    configured side pattern.
    """
    columns = max(1, hardware.tower_count())
    total = hardware.pod_capacity()
    per_column = -(-total // columns)  # ceil, so a short last column works
    index = max(0, int(pod_id) - 1)
    level = (index % per_column) + 1
    pattern = config.POD_SIDE_PATTERN or ""
    side = pattern[level - 1] if level <= len(pattern) else None
    return {"column": index // per_column + 1, "level": level, "side": side}


def with_positions(pods):
    """Return pods with their derived ``position`` attached, for the API."""
    out = []
    for pod in pods:
        entry = dict(pod)
        entry["position"] = position_for(pod["id"])
        out.append(entry)
    return out


def load_pods():
    try:
        with open(config.PODS_FILE) as fh:
            return normalize(json.load(fh))
    except (FileNotFoundError, ValueError):
        return default_pods()


def save_pods(pods):
    normalized = normalize(pods)
    write_json_atomic(config.PODS_FILE, normalized)
    return normalized


def set_pod(pod_id, name=None, symbols=None):
    """Update a single pod's name and/or symbols; returns the full pod list."""
    pod_id = int(pod_id)
    pods = load_pods()
    for pod in pods:
        if pod["id"] == pod_id:
            if name is not None:
                pod["name"] = str(name)[:MAX_NAME]
            if symbols is not None:
                pod["symbols"] = [s for s in symbols if s in SHAPES][:MAX_SYMBOLS]
            break
    return save_pods(pods)
