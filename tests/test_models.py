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

    def test_home_line_hardware(self):
        # The Home line is the max-yield architecture: 3 towers, 2 light bars,
        # 2 cameras, 30 pods, across every generation.
        for name in ("gardyn 1.0", "gardyn 2.0", "gardyn 3.0", "gardyn 4.0"):
            profile = models.profile_for(name)
            with self.subTest(model=name):
                self.assertEqual(profile["towers"], 3)
                self.assertEqual(profile["light_bars"], 2)
                self.assertEqual(profile["cameras"], 2)
                self.assertIs(profile["lower_camera"], True)
                self.assertEqual(profile["pods"], 30)

    def test_studio_line_hardware(self):
        # The Studio line is the trimmed profile for compact spaces: 2 towers,
        # 1 light bar, 1 camera, 16 pods.
        for name in ("gardyn studio", "gardyn studio 2"):
            profile = models.profile_for(name)
            with self.subTest(model=name):
                self.assertEqual(profile["towers"], 2)
                self.assertEqual(profile["light_bars"], 1)
                self.assertEqual(profile["cameras"], 1)
                self.assertIs(profile["lower_camera"], False)
                self.assertEqual(profile["pods"], 16)

    def test_home_and_studio_lines_differ(self):
        # The two lines must not collapse into the same hardware description.
        self.assertNotEqual(models.profile_for("gardyn 3.0"), models.profile_for("gardyn studio"))

    def test_3_0_overrides_sensor_only(self):
        self.assertEqual(models.Gardyn3.temp_humidity, "DHT20")
        # Cameras and layout are inherited from the Home line.
        self.assertIs(models.Gardyn3.lower_camera, models.Gardyn.lower_camera)
        self.assertEqual(models.Gardyn3.towers, 3)

    def test_undetermined_sensors_are_omitted(self):
        # Newer models have no confirmed chip yet; /system must omit the field
        # rather than claim a sensor we have not verified.
        for cls in (models.Gardyn4, models.GardynStudio2):
            with self.subTest(model=cls.name):
                self.assertIsNone(cls.temp_humidity)
                self.assertNotIn("temp_humidity", cls.profile())

    def test_registry_covers_every_generation(self):
        self.assertEqual(
            set(models.MODELS),
            {
                "gardyn 1.0",
                "gardyn 2.0",
                "gardyn 3.0",
                "gardyn 4.0",
                "gardyn studio",
                "gardyn studio 2",
            },
        )


class ModelForTestCase(unittest.TestCase):
    def test_exact_match(self):
        self.assertIs(models.model_for("gardyn studio"), models.GardynStudio)
        self.assertIs(models.model_for("gardyn 3.0"), models.Gardyn3)

    def test_suffixed_name_matches_closest_model(self):
        # The simulator reports 'gardyn 3.0 (simulated)'.
        self.assertIs(models.model_for("gardyn 3.0 (simulated)"), models.Gardyn3)

    def test_unknown_and_empty_fall_back_to_base(self):
        # A model we have no profile for behaves like the Home line.
        self.assertIs(models.model_for("gardyn 9.0"), models.Gardyn)
        self.assertIs(models.model_for(""), models.Gardyn)
        self.assertIs(models.model_for(None), models.Gardyn)

    def test_longest_name_wins_for_suffixed_studio(self):
        # 'gardyn studio 2' contains 'gardyn studio', so a naive substring scan
        # would resolve the 2nd generation to the 1st.
        self.assertIs(models.model_for("gardyn studio 2"), models.GardynStudio2)
        self.assertIs(models.model_for("gardyn studio 2 (simulated)"), models.GardynStudio2)
        self.assertIs(models.model_for("gardyn studio (simulated)"), models.GardynStudio)


class ProfileForTestCase(unittest.TestCase):
    def test_profile_shape_for_3_0(self):
        profile = models.profile_for("gardyn 3.0")
        self.assertEqual(profile["temp_humidity"], "DHT20")
        # The 3.0 is a Home-line unit: both cameras.
        self.assertIs(profile["lower_camera"], True)
        self.assertEqual(profile["cameras"], 2)

    def test_unknown_model_uses_base_defaults(self):
        profile = models.profile_for("gardyn 4.0")
        self.assertNotIn("temp_humidity", profile)
        self.assertIs(profile["lower_camera"], True)
        self.assertEqual(profile["cameras"], 2)

    def test_profile_is_a_fresh_dict_each_call(self):
        # Callers (e.g. the /system route) add env overrides on top.
        first = models.profile_for("gardyn studio")
        first["cameras"] = 99
        self.assertEqual(models.profile_for("gardyn studio")["cameras"], 1)


if __name__ == "__main__":
    unittest.main()
