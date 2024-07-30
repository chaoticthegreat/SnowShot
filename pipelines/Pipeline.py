import time
from typing import Tuple

import cv2
import numpy as np

from config.config import Configuration


class Pipeline:
    _video_pipeline = None

    def initialize(self, config: Configuration) -> bool:
        if self._video_pipeline is None:
            if config.cameraConfig.cameraID <= -1:
                print("Invalid camera ID")
                return False
            else:
                self._video_pipeline = cv2.VideoCapture('v4l2src device=/dev/video' + str(
                    config.cameraConfig.cameraID) + ' extra_controls=\"c,exposure_auto=' + str(
                    config.cameraConfig.cameraAutoExposure) + ',exposure_absolute=' + str(
                    config.cameraConfig.cameraExposure) + ',gain=' + str(
                    config.cameraConfig.cameraGain) + ',sharpness=0,brightness=' + str(
                    config.cameraConfig.cameraBrightness) + ',contrast=' + str(
                    config.cameraConfig.cameraContrast) + ',hue=' + str(
                    config.cameraConfig.cameraHue) + ',saturation=' + str(
                    config.cameraConfig.cameraSaturation) + '\" ! image/jpeg,format=MJPG,width=' + str(
                    config.cameraConfig.cameraResolutionWidth) + ',height=' + str(
                    config.cameraConfig.cameraResolutionHeight) + ' ! jpegdec ! video/x-raw ! appsink drop=1',
                                                        cv2.CAP_GSTREAMER)
                return True
        return False

    def reset_config(self, config: Configuration) -> None:
        if self._video_pipeline is not None:
            self._video_pipeline.release()
        self._video_pipeline = None
        time.sleep(1)
        self.initialize(config)

    def get_frame(self) -> Tuple[bool, cv2.Mat]: # note: change to UMat if you post process
        if self._video_pipeline is not None:
            return self._video_pipeline.read()
        return False, cv2.Mat(np.ndarray([]))

    def process_frame(self, frame: cv2.Mat):
        raise NotImplementedError

    def initialize_publisher(self, config: Configuration):
        raise NotImplementedError
    def send_to_nt(self, data: any, config: Configuration, timestamp: float):
        raise NotImplementedError
