import os

from flask import Blueprint, send_from_directory

# Serves the built-in single-page web UI (Web App Interface milestone #11).
# The page is plain HTML/JS that drives the existing REST endpoints, so the
# firmware ships a usable browser UI with no separate app required.
web_blueprint = Blueprint("web", __name__)

_WEB_DIR = os.path.dirname(__file__)


@web_blueprint.route("/", methods=["GET"])
def index():
    return send_from_directory(_WEB_DIR, "index.html")
