import unittest

from app.lib import models


class ModelDefaultsTestCase(unittest.TestCase):
    """Base Gardyn carries the usual defaults; generations override what differs."""

    def test_base_defaults(self):
        # Unknown sensor type: the env-driven driver decides, /system omits it.
        self.assertIsNone(models.Gardyn.temp_humidity)
        self.assertTrue(models.Gardyn.lower_camera)
        self.assertEqual(models.Gardyn.profile()["cameras"], 2)

    def test_early_models_keep_am2320_and_both_cameras(self):
        for cls in (models.Gardyn1, models.Gardyn2):
            self.assertEqual(cls.temp_humidity, "AM2320")
            self.assertTrue(cls.lower_camera)

    def test_3_0_overrides_sensor_and_camera(self):
        self.assertEqual(models.Gardyn3.temp_humidity, "DHT20")
        self.assertFalse(models.Gardyn3.lower_camera)
        self.assertEqual(models.Gardyn3.profile()["cameras"], 1)

    def test_studio_overrides_sensor_only(self):
        self.assertEqual(models.GardynStudio.temp_humidity, "DHT20")
        self.assertTrue(models.GardynStudio.lower_camera)
        # Unchanged fields are inherited from the base class.
        self.assertIs(models.GardynStudio.lower_camera, models.Gardyn.lower_camera)

    def test_registry_covers_every_generation(self):
        self.assertEqual(
            set(models.MODELS),
            {"gardyn 1.0", "gardyn 2.0", "gardyn 3.0", "gardyn studio"},
        )


class ModelForTestCase(unittest.TestCase):
    def test_exact_match(self):
        self.assertIs(models.model_for("gardyn studio"), models.GardynStudio)
        self.assertIs(models.model_for("gardyn 3.0"), models.Gardyn3)

    def test_suffixed_name_matches_closest_model(self):
        # The simulator reports 'gardyn 3.0 (simulated)'.
        self.assertIs(models.model_for("gardyn 3.0 (simulated)"), models.Gardyn3)

    def test_unknown_and_empty_fall_back_to_base(self):
        self.assertIs(models.model_for("gardyn 4.0"), models.Gardyn)
        self.assertIs(models.model_for(""), models.Gardyn)
        self.assertIs(models.model_for(None), models.Gardyn)


class ProfileForTestCase(unittest.TestCase):
    def test_profile_shape_for_3_0(self):
        profile = models.profile_for("gardyn 3.0")
        self.assertEqual(profile["temp_humidity"], "DHT20")
        self.assertIs(profile["lower_camera"], False)
        self.assertEqual(profile["cameras"], 1)

    def test_unknown_model_uses_base_defaults(self):
        profile = models.profile_for("gardyn 4.0")
        self.assertNotIn("temp_humidity", profile)
        self.assertIs(profile["lower_camera"], True)
        self.assertEqual(profile["cameras"], 2)

    def test_profile_is_a_fresh_dict_each_call(self):
        # Callers (e.g. the /system route) add env overrides on top.
        first = models.profile_for("gardyn studio")
        first["cameras"] = 99
        self.assertEqual(models.profile_for("gardyn studio")["cameras"], 2)


if __name__ == "__main__":
    unittest.main()
