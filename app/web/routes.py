import os

from flask import Blueprint, request, send_from_directory

# Serves the built-in single-page web UI (Web App Interface milestone #11).
# The page is plain HTML/JS that drives the existing REST endpoints, so the
# firmware ships a usable browser UI with no separate app required.
web_blueprint = Blueprint("web", __name__)

_WEB_DIR = os.path.dirname(__file__)
_ICON_DIR = os.path.join(_WEB_DIR, "icons")

# Icons live at the site root because that is where clients look for them
# without parsing the page: /favicon.ico (KeePassXC, Vaultwarden) and
# /apple-touch-icon*.png (Safari, iOS home screen). The inline data: URI the
# page used before only worked for browser tabs.
ICON_PATHS = {
    "/favicon.ico": "favicon.ico",
    "/favicon.svg": "favicon.svg",
    "/apple-touch-icon.png": "apple-touch-icon.png",
    "/apple-touch-icon-precomposed.png": "apple-touch-icon.png",
    "/icon-192.png": "icon-192.png",
    "/icon-512.png": "icon-512.png",
    "/site.webmanifest": "site.webmanifest",
}


@web_blueprint.route("/", methods=["GET"])
def index():
    return send_from_directory(_WEB_DIR, "index.html")


def icon():
    return send_from_directory(_ICON_DIR, ICON_PATHS[request.path], max_age=86400)


for _path in ICON_PATHS:
    web_blueprint.add_url_rule(_path, "icon", icon, methods=["GET"])
