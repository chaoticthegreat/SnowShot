import dataclasses
import time

import cv2
import ntcore
import numpy as np

from config.ConfigManager import load_calibration_config, load_nt_config, ConfigManager, config_changed
from config.config import Configuration, NetworkTablesConfig, CalibrationConfig, CameraConfig
from pipelines.ArucoPipeline import ArucoPipeline
from pipelines.CameraPoseEstimator import solve_camera_pose
from pipelines.Pipeline import Pipeline
from pipelines.PosePublisher import PosePublisher

CALIBRATION_FILENAME = "calibration.json"
CONFIG_FILENAME = "ntconfig.json"


def main():
    config_data = Configuration(NetworkTablesConfig(), CalibrationConfig(), CameraConfig())
    last_config = Configuration(NetworkTablesConfig(), CalibrationConfig(), CameraConfig())
    config_manager = ConfigManager()

    load_calibration_config(config_data, CALIBRATION_FILENAME)
    if config_data.calibConfig.cameraMatrix == np.array(
            []) or config_data.calibConfig.distortionCoefficients == np.array([]):
        raise Exception("Calibration not loaded!")
    load_nt_config(config_data, CONFIG_FILENAME)

    ntcore.NetworkTableInstance.getDefault().setServer(config_data.ntConfig.serverIP)
    ntcore.NetworkTableInstance.getDefault().startClient4(config_data.ntConfig.deviceID)
    config_manager.initialize_subscribers(config_data)

    pipeline: Pipeline = ArucoPipeline(cv2.aruco.DICT_APRILTAG_36h11)
    pipeline.initialize(config_data)
    pipeline.initialize_publisher(config_data)

    pose_publisher = PosePublisher()
    pose_publisher.initialize_publisher(config_data)

    frames = 0
    last_print = 0
    while True:
        last_config = Configuration(dataclasses.replace(config_data.ntConfig),
                                    dataclasses.replace(config_data.calibConfig),
                                    dataclasses.replace(config_data.cameraConfig))
        config_manager.update_camera_config(config_data)
        fps = None
        frames += 1
        if time.time() - last_print > 1:
            last_print = time.time()
            fps = frames
            print('Running at', frames, 'fps')
            frame_count = 0
        if config_changed(last_config, config_data):
            pipeline.reset_config(config_data)

        success, frame = pipeline.get_frame()
        if not success:
            pipeline.reset_config(config_data)
            continue
        tags = pipeline.process_frame(frame)
        poses = solve_camera_pose(tags, config_data.cameraConfig.tagLayout)

        pipeline.send_to_nt(tags, config_data, time.time())
        pose_publisher.send(time.time(), poses, fps)


if __name__ == "__main__":
    main()
