from flask import Flask
from .sensors.light.routes import light_blueprint
from .sensors.pump.routes import pump_blueprint
from .sensors.distance.routes import distance_blueprint
from .sensors.temperature.routes import temperature_blueprint
from .sensors.humidity.routes import humidity_blueprint
from .sensors.pcb_temp.routes import pcb_temp_blueprint

def create_app(config_name):
    app = Flask(__name__)

    # from your_flask_app.config import Config
    # app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(light_blueprint, url_prefix='/light')
    app.register_blueprint(pump_blueprint, url_prefix='/pump')
    app.register_blueprint(distance_blueprint, url_prefix='/distance')
    app.register_blueprint(temperature_blueprint, url_prefix='/temperature')
    app.register_blueprint(humidity_blueprint, url_prefix='/humidity')
    app.register_blueprint(pcb_temp_blueprint, url_prefix='/pcb-temp')

    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
        # pump_control = PumpControl()
        # pump_control.close()

    return app
