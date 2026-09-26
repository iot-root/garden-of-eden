"""Per-model Gardyn hardware descriptions.

Each generation is a small class that inherits shared defaults from the base
``Gardyn`` and overrides only what differs (issues #72, #84). This replaces the
``config.MODELS`` dict-of-dicts: the table was static code rather than
environment configuration, and a class hierarchy shows at a glance what makes
a 3.0 different from a Studio.

Resolution helpers (``model_for`` / ``profile_for``) keep the fuzzy matching
the old table had, so custom names like ``gardyn 3.0 (simulated)`` still map
to the closest known model; unknown models fall back to the base ``Gardyn``
defaults (both cameras, sensor type unknown).

Environment variables still take precedence over model defaults at runtime:
``SENSOR_TYPE`` picks the temp/humidity driver, ``LOWER_CAMERA_ENABLED``
overrides the camera layout (see ``app/lib/hardware.lower_camera_enabled``),
and ``GARDYN_MODEL`` forces the model instead of auto-detecting it.
"""


class Gardyn:
    """Defaults shared by every Gardyn generation.

    Override only what differs in a subclass. Keep values here only when they
    are intrinsic to the hardware; pins, addresses, thresholds, and paths stay
    env-driven in config.py (see CLAUDE.md).
    """

    # Model string as reported by /system and used for fuzzy matching.
    name = "gardyn"
    # Temp/humidity I2C chip. None = unknown: the actual driver is chosen by
    # config.SENSOR_TYPE, and /system omits the field for unknown models.
    temp_humidity = None
    # Most generations ship upper + lower cameras; the 3.0 ships upper only.
    lower_camera = True

    @classmethod
    def profile(cls):
        """Fresh JSON-friendly profile dict as served by /system."""
        profile = {}
        if cls.temp_humidity:
            profile["temp_humidity"] = cls.temp_humidity
        profile["cameras"] = 2 if cls.lower_camera else 1
        profile["lower_camera"] = cls.lower_camera
        return profile


class Gardyn1(Gardyn):
    """Original Gardyn: AM2320 sensor, both cameras."""

    name = "gardyn 1.0"
    temp_humidity = "AM2320"


class Gardyn2(Gardyn):
    """Second generation: AM2320 sensor, both cameras."""

    name = "gardyn 2.0"
    temp_humidity = "AM2320"


class Gardyn3(Gardyn):
    """Third generation: DHT20 sensor, upper camera only."""

    name = "gardyn 3.0"
    temp_humidity = "DHT20"
    lower_camera = False


class GardynStudio(Gardyn):
    """Studio: DHT20 sensor, upper camera only.

    Like the 3.0, the Studio has no lower camera. Confirmed on the hardware:
    a single USB capture node (``/dev/video0``, with ``/dev/video1`` as its
    companion metadata node) and no second camera present.
    """

    name = "gardyn studio"
    temp_humidity = "DHT20"
    lower_camera = False


# Known models keyed by their reported name.
MODELS = {m.name: m for m in (Gardyn1, Gardyn2, Gardyn3, GardynStudio)}


def model_for(model):
    """Resolve a model string to a model class.

    Exact match first, then prefix/substring so custom or suffixed names
    (e.g. 'gardyn 3.0 (simulated)') map to the closest known model. Unknown or
    empty names fall back to the base ``Gardyn`` defaults.
    """
    if not model:
        return Gardyn
    if model in MODELS:
        return MODELS[model]
    for key, cls in MODELS.items():
        if model.startswith(key) or key in model:
            return cls
    return Gardyn


def profile_for(model):
    """Return a fresh profile dict for a model string (see ``Gardyn.profile``).

    Always a new dict so callers (e.g. the /system route) can safely add the
    env overrides on top.
    """
    return model_for(model).profile()
