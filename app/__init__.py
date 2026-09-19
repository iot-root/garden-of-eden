import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

import config

from .sensors.camera.routes import camera_blueprint
from .sensors.distance.routes import distance_blueprint
from .sensors.grow.routes import grow_blueprint
from .sensors.humidity.routes import humidity_blueprint
from .sensors.light.routes import light_blueprint
from .sensors.pcb_temp.routes import pcb_temp_blueprint
from .sensors.pods.routes import pods_blueprint
from .sensors.pump.routes import pump_blueprint
from .sensors.schedule.routes import schedule_blueprint
from .sensors.system.routes import system_blueprint
from .sensors.temperature.routes import temperature_blueprint
from .web.routes import web_blueprint

logger = logging.getLogger(__name__)


def create_app(config_name=None):
    app = Flask(__name__)

    # CORS lives here (not run.py) so the test client and any WSGI host get
    # identical behavior.
    CORS(app)

    _register_auth(app)

    # Register blueprints
    app.register_blueprint(light_blueprint, url_prefix="/light")
    app.register_blueprint(pump_blueprint, url_prefix="/pump")
    app.register_blueprint(distance_blueprint, url_prefix="/distance")
    app.register_blueprint(temperature_blueprint, url_prefix="/temperature")
    app.register_blueprint(humidity_blueprint, url_prefix="/humidity")
    app.register_blueprint(pcb_temp_blueprint, url_prefix="/pcb-temp")
    app.register_blueprint(camera_blueprint, url_prefix="/camera")
    app.register_blueprint(schedule_blueprint, url_prefix="/schedule")
    app.register_blueprint(grow_blueprint, url_prefix="/grow")
    app.register_blueprint(pods_blueprint, url_prefix="/pods")
    app.register_blueprint(system_blueprint, url_prefix="/system")
    app.register_blueprint(web_blueprint)

    @app.route("/health")
    def health():
        return jsonify(status="ok"), 200

    return app


def _register_auth(app):
    """Optional API-key auth (issue #7).

    Enabled only when GARDEN_API_KEY is set. Localhost requests (e.g. the Pi's
    own cron jobs) and CORS preflight bypass the check so automation keeps
    working without a key.
    """
    if not config.GARDEN_API_KEY:
        return

    # The UI shell and static assets load without a key so the page can prompt
    # for one; API calls it makes still carry the key.
    @app.before_request
    def check_auth():
        if request.method == "OPTIONS":
            return None
        if request.remote_addr in ("127.0.0.1", "::1"):
            return None
        if request.path in ("/", "/health") or request.path.startswith("/static"):
            return None
        if request.headers.get("X-API-Key") != config.GARDEN_API_KEY:
            return jsonify(error="Unauthorized"), 401
        return None
