"""Single source of truth for logging setup across the REST API, the MQTT
service, and the standalone driver CLIs (issue #19)."""

import logging

import config

_configured = False


def configure_logging(to_file=True):
    """Configure root logging once: console always, file when ``to_file``.

    Level comes from ``LOG_LEVEL`` (default INFO); the log file from
    ``LOG_FILE``. Safe to call multiple times.
    """
    global _configured
    if _configured:
        return

    level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    handlers = [logging.StreamHandler()]
    if to_file:
        try:
            handlers.append(logging.FileHandler(config.LOG_FILE))
        except OSError:
            # Read-only filesystem / no permission: console-only is fine.
            pass

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    _configured = True
