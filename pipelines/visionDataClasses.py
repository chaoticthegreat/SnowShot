from dataclasses import dataclass
import numpy as np
import numpy.typing


@dataclass(frozen=True)
class Tag:
    tagID: int
    corners: np.typing.NDArray[np.float64]
