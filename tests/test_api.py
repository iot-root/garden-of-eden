import unittest
from unittest.mock import Mock, patch
from flask import json
from app import create_app
from parameterized import parameterized

class BaseTestCase(unittest.TestCase):
    
    def setUp(self):
        super().setUp() # This will call the setUp method of the BaseTestCase
        self.app = create_app('default')  
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

class PumpBlueprintTestCase(BaseTestCase):
    
    BASE_ROUTE = "/pump"

    # Parameterized test for /on and /off routes
    @parameterized.expand([
        ("/on", "on", "Pump turned on!"),
        ("/off", "off", "Pump turned off!")
    ])

    def test_pump_actions(self, route, mock_method, expected_message):
        mock_pump = Mock()
        with patch('app.sensors.pump.routes.pump_control', mock_pump):
            response = self.client.post(f'{self.BASE_ROUTE}{route}')
            self.assertEqual(response.status_code, 200)
            getattr(mock_pump, mock_method).assert_called_once()
            self.assertEqual(response.get_json(), {"message": expected_message})

    @patch('app.sensors.pump.routes.pump_control')
    def test_pump_turn_on(self, mock_pump):
        response = self.client.post(f'{self.BASE_ROUTE}/on')
        self.assertEqual(response.status_code, 200)
        mock_pump.on.assert_called_once()
        self.assertEqual(response.get_json(), {"message": "Pump turned on!"})

    @patch('app.sensors.pump.routes.pump_control')
    def test_pump_turn_off(self, mock_pump):
        response = self.client.post(f'{self.BASE_ROUTE}/off')
        self.assertEqual(response.status_code, 200)
        mock_pump.off.assert_called_once()
        self.assertEqual(response.get_json(), {"message": "Pump turned off!"})

    @patch('app.sensors.pump.routes.pump_control')
    def test_pump_adjust_speed(self, mock_pump):
        response = self.client.post(f'{self.BASE_ROUTE}/speed', json={"value": 50})
        self.assertEqual(response.status_code, 200)
        mock_pump.set_speed.assert_called_once_with(50)
        self.assertEqual(response.get_json(), {"message": "Pump adjusted to 50% speed!"})

    @patch('app.sensors.pump.routes.pump_control')
    def test_pump_get_speed(self, mock_pump):
        mock_pump.get_speed.return_value = 75
        response = self.client.get(f'{self.BASE_ROUTE}/speed')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"value": 75})

    @patch('app.sensors.pump.routes.fetch_ina219_data')
    @patch('app.sensors.pump.routes.pump_control')
    def test_pump_get_power_data(self, mock_pump, mock_fetch_data):
        mock_data = {"current": 5.2, "voltage": 12.5}
        mock_fetch_data.return_value = mock_data
        response = self.client.get(f'{self.BASE_ROUTE}/stats')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), mock_data)

    @patch('app.sensors.pump.routes.pump_control')
    def test_pump_adjust_speed_invalid(self, mock_pump):
        mock_pump.set_speed.side_effect = ValueError("Invalid speed value")
        response = self.client.post(f'{self.BASE_ROUTE}/speed', json={"value": 150})  # Assuming 150 is invalid
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "Invalid speed value"})

class LightBlueprintTestCase(BaseTestCase):
    
    BASE_ROUTE = "/light"

    def setUp(self):
        self.app = create_app('default')  
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    @patch('app.sensors.light.routes.light_control')
    def test_light_turn_on(self, mock_light):
        response = self.client.post(f'{self.BASE_ROUTE}/on')
        self.assertEqual(response.status_code, 200)
        mock_light.on.assert_called_once()
        self.assertEqual(response.get_json(), {"message": "Light turned on"})

    @patch('app.sensors.light.routes.light_control')
    def test_light_turn_off(self, mock_light):
        response = self.client.post(f'{self.BASE_ROUTE}/off')
        self.assertEqual(response.status_code, 200)
        mock_light.off.assert_called_once()
        self.assertEqual(response.get_json(), {"message": "Light turned off"})

    @patch('app.sensors.light.routes.light_control')
    def test_light_set_brightness(self, mock_light):
        response = self.client.post(f'{self.BASE_ROUTE}/brightness', json={"value": 75})
        self.assertEqual(response.status_code, 200)
        mock_light.set_brightness.assert_called_once_with(75)
        self.assertEqual(response.get_json(), {"message": "Light adjusted to 75%"})

    @patch('app.sensors.light.routes.light_control')
    def test_light_get_brightness(self, mock_light):
        mock_light.get_brightness.return_value = 60
        response = self.client.get(f'{self.BASE_ROUTE}/brightness')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"value": 60})

    @patch('app.sensors.light.routes.light_control')
    def test_light_set_brightness_invalid(self, mock_light):
        mock_light.set_brightness.side_effect = ValueError("Invalid brightness value")
        response = self.client.post(f'{self.BASE_ROUTE}/brightness', json={"value": 150})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"message": "Invalid brightness value"})

class DistanceBlueprintTestCase(BaseTestCase):
    
    BASE_ROUTE = "/distance"

    def setUp(self):
        self.app = create_app('default')
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    @patch('app.sensors.distance.routes.distance_control')
    def test_get_distance(self, mock_distance):
        # Mocking the return value of measure_once method to simulate a distance value of 55.5
        mock_distance.measure_once.return_value = 55.5

        # Making a GET request to the /measure endpoint
        response = self.client.get(f'{self.BASE_ROUTE}')

        # Asserting that the status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Asserting that the response JSON contains the mocked distance value
        self.assertEqual(response.get_json(), {"distance": 55.5})

class PCBTempBlueprintTestCase(BaseTestCase):

    BASE_ROUTE = "/pcb-temp"

    @patch('app.sensors.pcb_temp.routes.get_pcb_temperature')
    def test_get_pcb_temperature(self, mock_get_pcb_temperature):
        # Mocking the return value of get_pcb_temperature function to simulate a temperature value of 55.7
        mock_get_pcb_temperature.return_value = 55.7

        # Making a GET request to the pcb_temp endpoint
        response = self.client.get(f'{self.BASE_ROUTE}')

        # Asserting that the status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Asserting that the response JSON contains the mocked temperature value
        self.assertEqual(response.get_json(), {"pcb-temp": "55.70"})

class TemperatureBlueprintTestCase(BaseTestCase):

    BASE_ROUTE = "/temperature"

    @patch('app.sensors.temperature.routes.load_temperature_sensor')
    def test_get_temperature(self, mock_temperature_sensor):
        # Mocking the return value of get_value method to simulate a temperature value of 45.6
        mock_temperature_sensor.return_value.read.return_value = 45.6

        # Making a GET request to the temperature endpoint
        response = self.client.get(f'{self.BASE_ROUTE}')

        # Asserting that the status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Asserting that the response JSON contains the mocked temperature value
        self.assertEqual(response.get_json(), {"temperature": "45.60"})

class HumidityBlueprintTestCase(BaseTestCase):

    BASE_ROUTE = "/humidity"

    @patch('app.sensors.humidity.routes.load_humidity_sensor')
    def test_get_humidity(self, mock_humidity_sensor):
        # Mocking the return value of get_value method to simulate a humidity value of 45.6
        mock_humidity_sensor.return_value.read.return_value = 45.6

        # Making a GET request to the humidity endpoint
        response = self.client.get(f'{self.BASE_ROUTE}')

        # Asserting that the status code is 200 OK
        self.assertEqual(response.status_code, 200)

        # Asserting that the response JSON contains the mocked humidity value
        self.assertEqual(response.get_json(), {"humidity": "45.60"})

if __name__ == "__main__":
    unittest.main()
