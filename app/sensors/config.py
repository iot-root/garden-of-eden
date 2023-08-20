# coding=utf-8
# """
# Use config to set default values.
# """
# import os

# config = {}

# BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# # camera settings
# PHOTO_DIR = config.get('PHOTO_DIR', '/tmp/images')
# RESOLUTION = config.get('PHOTO_DIR', '2500x1900')
# OLD_IMAGE_1 = config.get('OLD_IMAGE_1', 'CAMERA_1_IMAGE.jpeg')
# OLD_IMAGE_2 = config.get('OLD_IMAGE_2', 'CAMERA_2_IMAGE.jpeg')
# MIN_IMAGE_SIZE = config.get('MIN_IMAGE_SIZE', 500 * 1024)

# # dimmer settings
# CHANNEL_DIMMER = config.get('CHANNEL_LED', 12)
# FREQ_DIMMER = config.get('DIMMER_FREQ', 250)
# INIT_DUTY_DIMMER = config.get('INIT_DUTY_DIMMER', 0)
# LAST_SECS_DIMMER = config.get('LAST_SECS_DIMMER', 20)

# # water pump switch settings
# CHANNEL_WATER_PUMP = config.get('CHANNEL_WATER_PUMP', 24)
# FREQ_WATER_PUMP = config.get('FREQ_WATER_PUMP', 50)
# INIT_DUTY_WATER_PUMP = config.get('INIT_DUTY_WATER_PUMP', 0)
# LAST_SECS_WATER_PUMP = config.get('LAST_SECS_WATER_PUMP', 30)
# MAX_DUTY_PUMP = config.get('MAX_DUTY_PUMP', 30)

# # water level settings
# CHANNEL_WATER_LVL_IN = config.get('CHANNEL_WATER_LVL_IN', 19)
# CHANNEL_WATER_LVL_OUT = config.get('CHANNEL_WATER_LVL_OUT', 26)
# TIMEOUT_WATER_LVL = config.get('TIMEOUT_WATER_LVL', 1)

# # LED settings
# CHANNEL_LED = config.get('CHANNEL_LED', 18)
# CHANNEL_BUTTON = config.get('CHANNEL_BUTTON', 13)
# FREQ_LED = config.get('FREQ_LED', 8000)
# INIT_DUTY_LED = config.get('INIT_DUTY_LED', 0)
# LAST_SECS_LIGHT_SWITCH = config.get('LAST_SECS_LIGHT_SWITCH', 60)
# RESET_THRESH = config.get('RESET_THRESH', 5)

# # Internal temp setting
# CHANNEL_TEMP_INTER = config.get('CHANNEL_TEMP_INTER', 25)
# THRESH_TEMP_INTER = config.get('THRESH_TEMP_INTER', 70)
