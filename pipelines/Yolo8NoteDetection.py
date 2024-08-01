import math
from typing import List

import cv2
import ntcore

from config.config import Configuration
from pipelines.Pipeline import Pipeline
from ultralytics import YOLO
import ultralytics

from pipelines.VisionDataClasses import YoloNoteDetection, YoloNoteDetection


def convert_to_tensorrt(model_path):
    model = YOLO(model_path)
    model.export(format="tensorrt")


class Yolo8NoteDetection(Pipeline):
    _detected_notes: ntcore.DoubleArrayPublisher

    def __init__(self, model_path, confidence_threshold):
        super().__init__()
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def process(self, frame: cv2.Mat) -> List[YoloNoteDetection]:
        results = self.model.track(frame, stream=True)
        detections = []
        for result in results:
            detections.append(
                YoloNoteDetection(confidence=result.confidence, box=result.boxes[0], latency=result.speed))
        return detections

    def initialize_publisher(self, config: Configuration):
        table = ntcore.NetworkTableInstance.getDefault().getTable("/" + config.ntConfig.deviceID + "/objectdetection")
        self._detected_notes = table.getDoubleArrayTopic("detected_notes").publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))

    def send_to_nt(self, data: List[YoloNoteDetection], config: Configuration, timestamp: float):
        if self._detected_notes is not None:
            publish_list: List[float] = [len(data)]
            for detection in data:
                publish_list += [detection.confidence, detection.box[0], detection.box[1], detection.box[2],
                                 detection.box[3], detection.latency]
            self._detected_notes.set(publish_list, math.floor(timestamp * 1000000))
