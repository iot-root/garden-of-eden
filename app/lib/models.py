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

Two hardware lines share this base. The **Home** line is the max-yield
architecture -- 3 towers, 2 full-spectrum LED light bars, 2 cameras, 30 pods --
and is carried by the base class, so an unrecognised unit still behaves like a
real machine rather than something arbitrary. The **Studio** line is the
trimmed profile for compact spaces: 2 towers, 1 light bar, 1 camera, 16 pods.

Environment variables still take precedence over model defaults at runtime:
``SENSOR_TYPE`` picks the temp/humidity driver, ``LOWER_CAMERA_ENABLED``
overrides the camera layout (see ``app/lib/hardware.lower_camera_enabled``),
and ``POD_COUNT`` / ``POD_COLUMNS`` override the pod layout. The model itself
comes from ``app.lib.hardware.detect_model``, in this order: a model chosen in
the web UI, then ``GARDYN_MODEL``, then inference from the sensor chip.
"""


class Gardyn:
    """Defaults shared by every Gardyn generation.

    Override only what differs in a subclass. Keep values here only when they
    are intrinsic to the hardware; pins, addresses, thresholds, and paths stay
    env-driven in config.py (see CLAUDE.md).

    The base class carries the Gardyn Home hardware, which is also the
    historical default for ``POD_COUNT``, so an unrecognised unit behaves like
    the highest-yield line rather than something arbitrary.
    """

    # Model string as reported by /system and used for fuzzy matching.
    name = "gardyn"
    # Temp/humidity I2C chip. None = unknown: the actual driver is chosen by
    # config.SENSOR_TYPE, and /system omits the field for unknown models.
    temp_humidity = None
    # Most generations ship upper + lower cameras.
    lower_camera = True
    # Physical layout of the unit. See the class docstring in this module for
    # the Home and Studio lines these describe.
    towers = 3
    light_bars = 2
    pods = 30

    @classmethod
    def profile(cls):
        """Fresh JSON-friendly profile dict as served by /system."""
        profile = {}
        if cls.temp_humidity:
            profile["temp_humidity"] = cls.temp_humidity
        profile["cameras"] = 2 if cls.lower_camera else 1
        profile["lower_camera"] = cls.lower_camera
        profile["towers"] = cls.towers
        profile["light_bars"] = cls.light_bars
        profile["pods"] = cls.pods
        return profile


class Gardyn1(Gardyn):
    """Home 1st generation: AM2320 sensor, both cameras, 3 towers."""

    name = "gardyn 1.0"
    temp_humidity = "AM2320"


class Gardyn2(Gardyn):
    """Home 2nd generation: AM2320 sensor, both cameras, 3 towers."""

    name = "gardyn 2.0"
    temp_humidity = "AM2320"


class Gardyn3(Gardyn):
    """Home 3rd generation: DHT20 sensor, both cameras, 3 towers."""

    name = "gardyn 3.0"
    temp_humidity = "DHT20"


class Gardyn4(Gardyn):
    """Home 4th generation: sensor not yet determined, both cameras, 3 towers."""

    name = "gardyn 4.0"


class GardynStudio(Gardyn):
    """Studio 1st generation: DHT20 sensor, upper camera only, 2 towers.

    The Studio line is the trimmed profile for compact spaces: 2 towers, 1
    light bar, 1 camera, 16 pods. Confirmed on the hardware, which exposes a
    single USB capture node (``/dev/video0``, with ``/dev/video1`` as its
    companion metadata node) and no second camera.
    """

    name = "gardyn studio"
    temp_humidity = "DHT20"
    lower_camera = False
    towers = 2
    light_bars = 1
    pods = 16


class GardynStudio2(GardynStudio):
    """Studio 2nd generation: same compact layout, sensor not yet determined."""

    name = "gardyn studio 2"
    temp_humidity = None


# Known models keyed by their reported name.
MODELS = {m.name: m for m in (Gardyn1, Gardyn2, Gardyn3, Gardyn4, GardynStudio, GardynStudio2)}


def model_for(model):
    """Resolve a model string to a model class.

    Exact match first, then prefix/substring so custom or suffixed names
    (e.g. 'gardyn 3.0 (simulated)') map to the closest known model. Unknown or
    empty names fall back to the base ``Gardyn`` defaults.

    Substring matching prefers the *longest* key, otherwise 'gardyn studio 2
    (simulated)' would resolve to 'gardyn studio', because the shorter name is
    contained in the longer one.
    """
    if not model:
        return Gardyn
    if model in MODELS:
        return MODELS[model]
    for key in sorted(MODELS, key=len, reverse=True):
        if model.startswith(key) or key in model:
            return MODELS[key]
    return Gardyn


def profile_for(model):
    """Return a fresh profile dict for a model string (see ``Gardyn.profile``).

    Always a new dict so callers (e.g. the /system route) can safely add the
    env overrides on top.
    """
    return model_for(model).profile()
