"""Single source of truth for logging setup across the REST API, the MQTT
service, and the standalone driver CLIs (issue #19)."""

import logging
import logging.handlers
import re
from collections import deque

import config

_configured = False

# Bounded in-memory ring of recent WARNING+ records, so a caller (currently the
# advice integration) can tell a model which parts of the machine are
# misbehaving -- e.g. a distance sensor that has stopped getting an echo, which
# makes the water reading derived from it untrustworthy. In-memory is
# deliberate: it only ever holds records emitted by this process, so it cannot
# pick up another service's log, and it costs nothing when nobody reads it.
_WARNINGS_MAX = 40
_warnings = deque(maxlen=_WARNINGS_MAX)

# These records are shipped to a third-party model, so anything that looks like
# a credential is stripped before it can enter the buffer. Log records are
# supposed to be safe, but a warning raised deep in a driver is not something
# this module can vouch for.
_SECRET_RE = re.compile(
    r"(sk-ant-[A-Za-z0-9_-]{6,}|gsk_[A-Za-z0-9]{6,}|Bearer\s+[A-Za-z0-9._-]{6,})"
)


def _redact(text):
    return _SECRET_RE.sub("[redacted]", str(text))


# logging.Handler has no formatTime(); that method lives on Formatter, so the
# handler borrows one to stamp records with a wall-clock time.
_time_formatter = logging.Formatter()


class RecentWarningHandler(logging.Handler):
    """Keep the most recent WARNING+ records in the bounded buffer above.

    The level is pinned to WARNING explicitly: a handler left at NOTSET would
    also capture INFO, which would fill the buffer with routine refresh chatter
    and crowd out the actual faults this exists to surface.
    """

    def __init__(self, level=logging.WARNING):
        super().__init__(level=level)

    def emit(self, record):
        try:
            # logging.Handler has no formatTime; that lives on Formatter.
            _warnings.append(
                {
                    "time": _time_formatter.formatTime(record, "%H:%M:%S"),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": _redact(record.getMessage())[:300],
                }
            )
        except Exception:  # noqa: BLE001 - logging must never break a caller
            pass


def recent_warnings(limit=10):
    """Return up to ``limit`` recent WARNING+ records, oldest first.

    Returns an empty list when :func:`configure_logging` has not run, since the
    handler that fills the buffer is installed there.
    """
    if limit <= 0:
        return []
    return [dict(entry) for entry in list(_warnings)[-limit:]]


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
    handlers = [logging.StreamHandler(), RecentWarningHandler()]

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
