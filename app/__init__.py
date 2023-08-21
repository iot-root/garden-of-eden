from flask import Flask
from .sensors.light.routes import light
from .sensors.pump.routes import pump
from .sensors.distance.routes import distance
from .sensors.pump.pump import Pump as PumpControl 

def create_app(config_name):
    app = Flask(__name__)

    # You could use a configuration setup like:
    # from your_flask_app.config import Config
    # app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(light, url_prefix='/light')
    app.register_blueprint(pump, url_prefix='/pump')
    app.register_blueprint(distance, url_prefix='/distance')
    app.register_blueprint(temperature, url_prefix='/temperature')
    app.register_blueprint(humidity, url_prefix='/humidity')

    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
        # pump_control = PumpControl()
        # pump_control.close()

    return app
