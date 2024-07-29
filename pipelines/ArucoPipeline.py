import math
from typing import List

import cv2
import ntcore

from config.config import Configuration
from pipelines.Pipeline import Pipeline
from pipelines.visionDataClasses import Tag


class ArucoPipeline(Pipeline):
    _tag_id_pub: ntcore.DoubleArrayPublisher
    _tag_center_pub: ntcore.DoubleArrayPublisher

    def __init__(self, dictionary_id) -> None:
        self._aruco_dict = cv2.aruco.getPredefinedDictionary(dictionary_id)
        self._aruco_params = cv2.aruco.DetectorParameters()
        self._aruco_detector = cv2.aruco.ArucoDetector(self._aruco_dict, self._aruco_params)

    def process_frame(self, frame: cv2.Mat) -> List[Tag]:
        corners, ids, _ = self._aruco_detector.detectMarkers(frame)

        if len(corners) == 0:
            return []
        return [Tag(tag_id[0], corner) for tag_id, corner in zip(ids, corners)]

    def initialize_publisher(self, config: Configuration):
        table = ntcore.NetworkTableInstance.getDefault().getTable("/" + config.ntConfig.deviceID + "/apriltags")
        self._tag_id_pub = table.getDoubleArrayTopic("tag_id").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))
        self._tag_center_pub = table.getDoubleArrayTopic("tag_center").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))

    def send_to_nt(self, data: List[Tag], config: Configuration, timestamp: float):
        if self._tag_id_pub is not None:
            self._tag_id_pub.set([tag.tagID for tag in data], math.floor(timestamp * 1000000))
        if self._tag_center_pub is not None:
            tag_centers = []
            for tag in data:
                x_sum = tag.corners[0][0][0][0] + tag.corners[0][0][1][0] + tag.corners[0][0][2][0] + \
                        tag.corners[0][0][3][0]
                y_sum = tag.corners[0][0][0][1] + tag.corners[0][0][1][1] + tag.corners[0][0][2][1] + \
                        tag.corners[0][0][3][1]

                x_centerPixel = x_sum * .25
                y_centerPixel = y_sum * .25
                tag_centers.append(x_centerPixel)
                tag_centers.append(y_centerPixel)
            self._tag_center_pub.set(tag_centers, math.floor(timestamp * 1000000))
