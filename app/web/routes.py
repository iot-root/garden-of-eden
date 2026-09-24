import os

from flask import Blueprint, Response

# Serves the built-in single-page web UI (Web App Interface milestone #11).
# The page is plain HTML/JS that drives the existing REST endpoints, so the
# firmware ships a usable browser UI with no separate app required.
# Read the file once into memory and return it directly so the test server does
# not leave the HTML file handle open and trigger ResourceWarning.
web_blueprint = Blueprint("web", __name__)

_WEB_DIR = os.path.dirname(__file__)


@web_blueprint.route("/", methods=["GET"])
def index():
    index_path = os.path.join(_WEB_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as fh:
        return Response(fh.read(), mimetype="text/html")
