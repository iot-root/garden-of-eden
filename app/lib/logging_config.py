"""Single source of truth for logging setup across the REST API, the MQTT
service, and the standalone driver CLIs (issue #19)."""

import logging
import logging.handlers

import config

_configured = False


def configure_logging(to_file=True, log_file=None):
    """Configure root logging once: console always, a rotating file when enabled.

    Level comes from ``LOG_LEVEL`` (default INFO). The file path is ``log_file``
    when given, else ``config.LOG_FILE``. Pass a distinct ``log_file`` per
    process (e.g. ``mqtt.log`` vs ``garden-api.log``) so the services don't write
    the same file concurrently. The file rotates (1 MB x 3 backups) so it can't
    grow unbounded, and an empty path disables file logging (rely on journald).
    Safe to call multiple times.
    """
    global _configured
    if _configured:
        return

    level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    handlers = [logging.StreamHandler()]

    path = log_file if log_file is not None else config.LOG_FILE
    if to_file and path:
        try:
            handlers.append(
                logging.handlers.RotatingFileHandler(path, maxBytes=1_000_000, backupCount=3)
            )
        except OSError:
            # Read-only filesystem / no permission: console-only is fine.
            pass

    # force=True tears down any root handler a module accidentally installed by
    # calling logging.* at import time (which auto-runs basicConfig at WARNING
    # with the default format) — otherwise our handlers/level/format are a no-op
    # and INFO logs get swallowed.
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )
    _configured = True
