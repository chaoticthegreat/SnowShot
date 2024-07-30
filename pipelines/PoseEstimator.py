import math
from typing import List, Union

import cv2
import numpy as np
import numpy.typing
from wpimath.geometry import Translation3d, Pose3d, Rotation3d, Quaternion, Transform3d

from config.config import Configuration
from pipelines.VisionDataClasses import TagObservation, PoseOutput, AprilTag

# cv2 to WPILib converter stolen from 6328 Northstar
def cv2pose_to_wpi(tvec: np.typing.NDArray[np.float64], rvec: np.typing.NDArray[np.float64]) -> Pose3d:
    return Pose3d(
        Translation3d(tvec[2][0], -tvec[0][0], -tvec[1][0]),
        Rotation3d(
            np.array([rvec[2][0], -rvec[0][0], -rvec[1][0]]),
            math.sqrt(math.pow(rvec[0][0], 2) + math.pow(rvec[1][0], 2) + math.pow(rvec[2][0], 2))
        ))


def convert_corners_to_list(tag: TagObservation) -> List[List[float]]:
    return [
        [tag.corners[0][0][0], tag.corners[0][0][1]],
        [tag.corners[0][1][0], tag.corners[0][1][1]],
        [tag.corners[0][2][0], tag.corners[0][2][1]],
        [tag.corners[0][3][0], tag.corners[0][3][1]]
    ]


def convert_to_opencv_pose(pose: Pose3d) -> List[float]:
    return [-pose.translation().Y(), -pose.translation().Z(), pose.translation().X()]


def create_object_points(tag_pose: Pose3d, tag_size: float) -> List[List[float]]:
    transform1 = Transform3d(Translation3d(0, tag_size / 2.0, -tag_size / 2.0), Rotation3d())
    transform2 = Transform3d(Translation3d(0, -tag_size / 2.0, -tag_size / 2.0), Rotation3d())
    transform3 = Transform3d(Translation3d(0, -tag_size / 2.0, tag_size / 2.0), Rotation3d())
    transform4 = Transform3d(Translation3d(0, tag_size / 2.0, tag_size / 2.0), Rotation3d())
    return [
        convert_to_opencv_pose(tag_pose.transformBy(transform1)),
        convert_to_opencv_pose(tag_pose.transformBy(transform2)),
        convert_to_opencv_pose(tag_pose.transformBy(transform3)),
        convert_to_opencv_pose(tag_pose.transformBy(transform4))
    ]

# Solver stolen from PhotonVision
def solve_camera_pose(image_observations: List[TagObservation], config: Configuration) -> Union[
    PoseOutput, None]:
    # Exit if no tag layout available
    if config.cameraConfig.tagLayout is None:
        return None

    # Exit if no observations available
    if len(image_observations) == 0:
        return None

    tag_list = []
    corners_list = []
    object_points = []
    tag_pose = None
    for tag in image_observations:
        for tag_layout in config.cameraConfig.tagLayout:
            if tag.tagID == tag_layout.tagID:
                tag_pose = Pose3d(
                    Translation3d(
                        tag_layout['pose']['translation']['x'],
                        tag_layout['pose']['translation']['y'],
                        tag_layout['pose']['translation']['z']
                    ),
                    Rotation3d(Quaternion(
                        tag_layout['pose']['rotation']['quaternion']['W'],
                        tag_layout['pose']['rotation']['quaternion']['X'],
                        tag_layout['pose']['rotation']['quaternion']['Y'],
                        tag_layout['pose']['rotation']['quaternion']['Z']
                    )))
        if tag_pose is None:
            continue
        tag_list.append(AprilTag(tag.tagID, tag_pose))
        corners_list.append(convert_corners_to_list(tag))
        object_points.append(create_object_points(tag_pose, config.cameraConfig.tagSize))
    if len(tag_list) == 0 or len(corners_list) == 0 or len(corners_list) % 4 != 0:
        return None
    if len(tag_list) == 1:
        object_points = np.array([[-config.cameraConfig.tagSize / 2.0, config.cameraConfig.tagSize / 2.0, 0.0],
                                  [config.cameraConfig.tagSize / 2.0, config.cameraConfig.tagSize / 2.0, 0.0],
                                  [config.cameraConfig.tagSize / 2.0, -config.cameraConfig.tagSize / 2.0, 0.0],
                                  [-config.cameraConfig.tagSize / 2.0, -config.cameraConfig.tagSize / 2.0, 0.0]])
        try:
            _, rvecs, tvecs, errors = cv2.solvePnPGeneric(object_points, np.array(corners_list),
                                                           config.calibConfig.cameraMatrix,
                                                           config.calibConfig.distortionCoefficients,
                                                           flags=cv2.SOLVEPNP_IPPE_SQUARE)
        except:
            return None
        bestTransform = cv2pose_to_wpi(tvecs[0], rvecs[0])
        secondTransform = cv2pose_to_wpi(tvecs[1], rvecs[1])
        bestPose = tag_list[0].pose.transformBy(Transform3d(bestTransform.translation(), bestTransform.rotation()).inverse())
        secondPose = tag_list[0].pose.transformBy(Transform3d(secondTransform.translation(), secondTransform.rotation()).inverse())

        return PoseOutput(Pose3d(bestPose.translation(), bestPose.rotation()), errors[0], Pose3d(secondPose.translation(), secondPose.rotation()), errors[1])

    # Multi-tag, return one pose
    else:
        # Run SolvePNP with all tags
        try:
            _, rvecs, tvecs, errors = cv2.solvePnPGeneric(np.array(object_points), np.array(corners_list),
                                                           config.local_config.cameraMatrix,
                                                           config.local_config.distortionCoefficients,
                                                           flags=cv2.SOLVEPNP_SQPNP)
        except:
            return None
        bestTransform = cv2pose_to_wpi(tvecs[0], rvecs[0])
        bestPose = tag_list[0].pose.transformBy(Transform3d(bestTransform.translation(), bestTransform.rotation()).inverse())
        return PoseOutput(Pose3d(bestPose.translation(), bestPose.rotation()), errors[0], None, None)

