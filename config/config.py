from dataclasses import dataclass
import numpy as np
import numpy.typing


@dataclass
class NetworkTablesConfig:
    deviceID: str = ''
    serverIP: str = ''
    streamPort: int = 8000


@dataclass
class CalibrationConfig:
    cameraMatrix: np.typing.NDArray[np.float64] = np.array([])
    distortionCoefficients: np.typing.NDArray[np.float64] = np.array([])


@dataclass
class NTConfig:
    cameraID: int = 0
    cameraResolutionWidth: int = 1080
    cameraResolutionHeight: int = 720
    cameraAutoExposure: int = 1
    cameraExposure: int = 20
    cameraGain: int = 25
    cameraContrast: int = 1
    cameraBrightness: int = 0
    cameraHue: int = 0
    cameraSaturation: int = 0
    tagSize: float = 0.2
    tagLayout: any = None
