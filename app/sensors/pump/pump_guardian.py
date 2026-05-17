import threading
import time
import logging

logger = logging.getLogger(__name__)

GUARDIAN_CHECK_INTERVAL_SECONDS = 30


class PumpGuardian:
    def __init__(self, pump_off_fn, mqtt_publish_fn, base_topic, max_on_seconds):
        self._pump_off_fn = pump_off_fn
        self._mqtt_publish_fn = mqtt_publish_fn
        self._base_topic = base_topic
        self._max_on_seconds = max_on_seconds
        self._pump_start_time = None
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def on_pump_on(self):
        with self._lock:
            self._pump_start_time = time.time()

    def on_pump_off(self):
        with self._lock:
            self._pump_start_time = None

    def _run(self):
        while True:
            time.sleep(GUARDIAN_CHECK_INTERVAL_SECONDS)
            with self._lock:
                if self._pump_start_time is None:
                    continue
                elapsed = time.time() - self._pump_start_time
                if elapsed > self._max_on_seconds:
                    logger.warning(
                        f"PumpGuardian: pump has been on for {elapsed:.0f}s, forcing off"
                    )
                    try:
                        self._pump_off_fn()
                        self._mqtt_publish_fn(self._base_topic + "/pump/state", "OFF")
                        self._mqtt_publish_fn("gardyn/pump/guardian", "forced_off")
                    except Exception as e:
                        logger.error(f"PumpGuardian: error forcing pump off: {e}")
                    self._pump_start_time = None
