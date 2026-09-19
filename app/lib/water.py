"""Water-level helpers shared by the MQTT service and REST API.

The distance sensor reports the gap (cm) from the sensor down to the water
surface, so a *larger* distance means a *lower* tank.
"""


def is_water_low(distance_cm, threshold_cm):
    """Return True if the tank is low.

    ``threshold_cm`` of ``None``/0 means alerting is disabled -> never low.
    A ``distance_cm`` of ``None`` (failed reading) is treated as "not low" so a
    sensor glitch doesn't raise a false alarm.
    """
    if not threshold_cm:
        return False
    if distance_cm is None:
        return False
    return distance_cm > threshold_cm


def gallons_remaining(distance_cm, full_cm, empty_cm, capacity_gal):
    """Estimate gallons left from the sensor distance via a linear full->empty map.

    ``full_cm`` is the distance when the tank is full (small), ``empty_cm`` when
    empty (large). Returns None on a bad reading or invalid calibration; clamps
    to the 0..capacity range otherwise.
    """
    if distance_cm is None or not capacity_gal:
        return None
    span = empty_cm - full_cm
    if span <= 0:
        return None
    fraction = (empty_cm - distance_cm) / span
    fraction = max(0.0, min(1.0, fraction))
    return round(fraction * capacity_gal, 1)
