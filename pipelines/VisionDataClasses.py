from dataclasses import dataclass
from typing import Union

import numpy as np
import numpy.typing
import wpimath.geometry


@dataclass(frozen=True)
class Tag:
    tagID: int
    corners: np.typing.NDArray[np.float64]

@dataclass(frozen=True)
class Poses:
    pose1: wpimath.geometry.Pose3d
    pose2: Union[wpimath.geometry.Pose3d, None]
