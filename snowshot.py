from config.ConfigManager import load_calibration_config, load_nt_config, ConfigManager
from config.config import Configuration, NetworkTablesConfig, CalibrationConfig, CameraConfig

CALIBRATION_FILENAME = "calibration.json"
CONFIG_FILENAME = "ntconfig.json"
def main():
    config_data = Configuration(NetworkTablesConfig(), CalibrationConfig(), CameraConfig())

    config_manager = ConfigManager()

    load_calibration_config(config_data, CALIBRATION_FILENAME)
    load_nt_config(config_data, CONFIG_FILENAME)
    config_manager.initialize_subscribers(config_data)
    while True:
        config_manager.update_camera_config(config_data)
