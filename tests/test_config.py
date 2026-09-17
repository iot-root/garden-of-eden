import importlib
import os
import unittest


class ConfigParsingTestCase(unittest.TestCase):
    """config.py uses helpers to parse env vars; verify hex/bool/int parsing."""

    def _reload(self, **env):
        for k, v in env.items():
            os.environ[k] = v
        try:
            import config

            return importlib.reload(config)
        finally:
            for k in env:
                os.environ.pop(k, None)

    def test_hex_address_parsing(self):
        cfg = self._reload(PCB_TEMP_ADDRESS="0x48", INA219_ADDRESS="0x40")
        self.assertEqual(cfg.PCB_TEMP_ADDRESS, 0x48)
        self.assertEqual(cfg.INA219_ADDRESS, 0x40)

    def test_decimal_pin_parsing(self):
        cfg = self._reload(LIGHT_PIN="18", PUMP_PIN="24")
        self.assertEqual(cfg.LIGHT_PIN, 18)
        self.assertEqual(cfg.PUMP_PIN, 24)

    def test_bool_parsing(self):
        cfg = self._reload(TELEGRAF_ENABLED="true", ALEXA_ENABLED="0")
        self.assertTrue(cfg.TELEGRAF_ENABLED)
        self.assertFalse(cfg.ALEXA_ENABLED)

    def test_water_low_zero_disables(self):
        cfg = self._reload(WATER_LOW_CM="0")
        self.assertIsNone(cfg.WATER_LOW_CM)


if __name__ == "__main__":
    unittest.main()
