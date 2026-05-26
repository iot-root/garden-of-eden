from flask import jsonify
from functools import wraps

def sensor_provider(func):
    func._is_sensor_provider = True
    return func

def check_sensor_guard(sensor, sensor_name):
    def decorator(func):
        # helps to maintain the wrapped functions metadata, otherwise Flask will complain about duplicate routes
        @wraps(func)
        def check_sensor(*args, **kwargs):
            current_sensor = sensor() if getattr(sensor, '_is_sensor_provider', False) else sensor
            if current_sensor == None:
                return jsonify(error=f'{sensor_name} are not initialized'), 400
            return func(*args, **kwargs)
        return check_sensor
    return decorator
