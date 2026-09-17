#!/usr/bin/env python3
from app import create_app
from app.lib.logging_config import configure_logging

configure_logging(log_file="garden-api.log")

app = create_app("default")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
