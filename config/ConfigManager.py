import json

import ntcore
import numpy as np

from config.config import Configuration


def load_calibration_config(config: Configuration, calibration_filename: str) -> None:
    with open(calibration_filename, 'r') as f:
        data = json.load(f)
        config.calibConfig.cameraMatrix = np.array(data['cameraMatrix'])
        config.calibConfig.distortionCoefficients = np.array(data['distortionCoefficients'])


def load_nt_config(config: Configuration, config_filename: str) -> None:
    with open(config_filename, 'r') as f:
        data = json.load(f)
        config.ntConfig.deviceID = data['deviceID']
        config.ntConfig.serverIP = data['serverIP']
        config.ntConfig.streamPort = data['streamPort']


class ConfigManager():
    _camera_id: ntcore.IntegerSubscriber
    _camera_resolution_width: ntcore.IntegerSubscriber
    _camera_resolution_height: ntcore.IntegerSubscriber
    _camera_auto_exposure: ntcore.IntegerSubscriber
    _camera_exposure: ntcore.IntegerSubscriber
    _camera_gain: ntcore.IntegerSubscriber
    _camera_contrast: ntcore.IntegerSubscriber
    _camera_brightness: ntcore.IntegerSubscriber
    _camera_hue: ntcore.IntegerSubscriber
    _camera_saturation: ntcore.IntegerSubscriber
    _tag_size: ntcore.DoubleSubscriber
    _tag_layout: ntcore.StringSubscriber

    def initialize_subscribers(self, config: Configuration) -> None:
        nt_table = ntcore.NetworkTableInstance.getDefault().getTable("/" + config.ntConfig.deviceID + "/configuration")
        self._camera_id = nt_table.getIntegerTopic("camera_id").subscribe(config.cameraConfig.cameraID)
        self._camera_resolution_width = nt_table.getIntegerTopic("camera_resolution_width").subscribe(
            config.cameraConfig.cameraResolutionWidth)
        self._camera_resolution_height = nt_table.getIntegerTopic("camera_resolution_height").subscribe(
            config.cameraConfig.cameraResolutionHeight)
        self._camera_auto_exposure = nt_table.getIntegerTopic("camera_auto_exposure").subscribe(
            config.cameraConfig.cameraAutoExposure)
        self._camera_exposure = nt_table.getIntegerTopic("camera_exposure").subscribe(
            config.cameraConfig.cameraExposure)
        self._camera_gain = nt_table.getIntegerTopic("camera_gain").subscribe(config.cameraConfig.cameraGain)
        self._camera_contrast = nt_table.getIntegerTopic("camera_contrast").subscribe(
            config.cameraConfig.cameraContrast)
        self._camera_brightness = nt_table.getIntegerTopic("camera_brightness").subscribe(
            config.cameraConfig.cameraBrightness)
        self._camera_hue = nt_table.getIntegerTopic("camera_hue").subscribe(config.cameraConfig.cameraHue)
        self._camera_saturation = nt_table.getIntegerTopic("camera_saturation").subscribe(
            config.cameraConfig.cameraSaturation)
        self._tag_size = nt_table.getDoubleTopic("tag_size").subscribe(config.cameraConfig.tagSize)
        self._tag_layout = nt_table.getStringTopic("tag_layout").subscribe(config.cameraConfig.tagLayout)

    def update_camera_config(self, config: Configuration) -> None:
        config.cameraConfig.cameraID = self._camera_id.get()
        config.cameraConfig.cameraResolutionWidth = self._camera_resolution_width.get()
        config.cameraConfig.cameraResolutionHeight = self._camera_resolution_height.get()
        config.cameraConfig.cameraAutoExposure = self._camera_auto_exposure.get()
        config.cameraConfig.cameraExposure = self._camera_exposure.get()
        config.cameraConfig.cameraGain = self._camera_gain.get()
        config.cameraConfig.cameraContrast = self._camera_contrast.get()
        config.cameraConfig.cameraBrightness = self._camera_brightness.get()
        config.cameraConfig.cameraHue = self._camera_hue.get()
        config.cameraConfig.cameraSaturation = self._camera_saturation.get()
        config.cameraConfig.tagSize = self._tag_size.get()
        try:
            config.cameraConfig.tagLayout = json.loads(self._tag_layout.get())
        except:
            config.cameraConfig.tagLayout = None
