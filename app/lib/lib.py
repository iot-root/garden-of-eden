from flask import jsonify
from functools import wraps

def check_sensor_guard(sensor, sensor_name):
    def decorator(func):
        # helps to maintain the wrapped functions metadata, otherwise Flask will complain about duplicate routes
        @wraps(func)
        def check_sensor(*args, **kwargs):
            if sensor == None:
                return jsonify(error=f'{sensor_name} are not initialized'), 400
            return func(*args, **kwargs)
        return check_sensor
    return decorator