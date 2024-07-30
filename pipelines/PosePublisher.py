import math
from typing import Union, List

import ntcore

from config.config import Configuration
from pipelines.VisionDataClasses import PoseOutput


class PosePublisher():
    _observations_pub: ntcore.DoubleArrayPublisher
    _fps_pub: ntcore.IntegerPublisher

    def initialize_publisher(self, config: Configuration):
        nt_table = ntcore.NetworkTableInstance.getDefault().getTable(
            '/' + config.local_config.device_id + '/output')
        self._observations_pub = nt_table.getDoubleArrayTopic('poses').publish(
            ntcore.PubSubOptions(periodic=0, sendAll=True, keepDuplicates=True))
        self._fps_pub = nt_table.getIntegerTopic('fps').publish()

    def send(self, timestamp: float, observation: Union[PoseOutput, None],
             fps: Union[int, None] = None) -> None:
        # Initialize publishers on first call
        # Send data
        if fps is not None:
            self._fps_pub.set(fps)
        observation_data: List[float] = [0]
        if observation is not None:
            observation_data[0] = 1
            observation_data.append(observation.error1)
            observation_data.append(observation.pose1.translation().X())
            observation_data.append(observation.pose1.translation().Y())
            observation_data.append(observation.pose1.translation().Z())
            observation_data.append(observation.pose1.rotation().getQuaternion().W())
            observation_data.append(observation.pose1.rotation().getQuaternion().X())
            observation_data.append(observation.pose1.rotation().getQuaternion().Y())
            observation_data.append(observation.pose1.rotation().getQuaternion().Z())
            if observation.pose2 is not None:
                observation_data[0] = 2
                observation_data.append(observation.error2)
                observation_data.append(observation.pose2.translation().X())
                observation_data.append(observation.pose2.translation().Y())
                observation_data.append(observation.pose2.translation().Z())
                observation_data.append(observation.pose2.rotation().getQuaternion().W())
                observation_data.append(observation.pose2.rotation().getQuaternion().X())
                observation_data.append(observation.pose2.rotation().getQuaternion().Y())
                observation_data.append(observation.pose2.rotation().getQuaternion().Z())
        self._observations_pub.set(observation_data, math.floor(timestamp * 1000000))
