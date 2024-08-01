from dataclasses import dataclass
from typing import Union, List

import numpy as np
import numpy.typing
import wpimath.geometry


@dataclass(frozen=True)
class TagObservation:
    tagID: int
    corners: np.typing.NDArray[np.float64]


@dataclass(frozen=True)
class PoseOutput:
    pose1: wpimath.geometry.Pose3d
    error1: float
    pose2: Union[wpimath.geometry.Pose3d, None]
    error2: Union[float, None]


@dataclass(frozen=True)
class AprilTag:
    tagID: int
    pose: wpimath.geometry.Pose3d


@dataclass(frozen=True)
class YoloNoteDetection:
    confidence: float
    box: List[float]  # in format xyxy
    latency: float