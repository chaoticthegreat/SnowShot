import math
from typing import List, Union

import cv2
import numpy as np
from wpimath.geometry import *
import numpy as np
import numpy.typing

from config.config import Configuration
from pipelines.VisionDataClasses import Poses, Tag

# Stolen from 6328 Northstar
def openCVPoseToWPILib(tvec: np.typing.NDArray[np.float64], rvec: np.typing.NDArray[np.float64]) -> Pose3d:
    return Pose3d(
        Translation3d(tvec[2][0], -tvec[0][0], -tvec[1][0]),
        Rotation3d(
            np.array([rvec[2][0], -rvec[0][0], -rvec[1][0]]),
            math.sqrt(math.pow(rvec[0][0], 2) + math.pow(rvec[1][0], 2) + math.pow(rvec[2][0], 2))
        ))


def wpiLibTranslationToOpenCV(translation: Translation3d) -> List[float]:
    return [-translation.Y(), -translation.Z(), translation.X()]


def solve_camera_pose(image_observations: List[Tag], config: Configuration) -> Union[
    Poses, None]:
    # Exit if no tag layout available
    if config.cameraConfig.tagLayout is None:
        return None

    # Exit if no observations available
    if len(image_observations) == 0:
        return None

    # Create set of object and image points
    tag_size = config.cameraConfig.tagSize
    object_points = []
    image_points = []
    tag_ids = []
    tag_poses = []
    for observation in image_observations:
        tag_pose = None
        for tag_data in config.cameraConfig.tagLayout['tags']:
            if tag_data['ID'] == observation.tagID:
                tag_pose = Pose3d(
                    Translation3d(
                        tag_data['pose']['translation']['x'],
                        tag_data['pose']['translation']['y'],
                        tag_data['pose']['translation']['z']
                    ),
                    Rotation3d(Quaternion(
                        tag_data['pose']['rotation']['quaternion']['W'],
                        tag_data['pose']['rotation']['quaternion']['X'],
                        tag_data['pose']['rotation']['quaternion']['Y'],
                        tag_data['pose']['rotation']['quaternion']['Z']
                    )))
        if tag_pose is not None:
            # Add object points by transforming from the tag center
            corner_0 = tag_pose + Transform3d(Translation3d(0, tag_size / 2.0, -tag_size / 2.0), Rotation3d())
            corner_1 = tag_pose + Transform3d(Translation3d(0, -tag_size / 2.0, -tag_size / 2.0), Rotation3d())
            corner_2 = tag_pose + Transform3d(Translation3d(0, -tag_size / 2.0, tag_size / 2.0), Rotation3d())
            corner_3 = tag_pose + Transform3d(Translation3d(0, tag_size / 2.0, tag_size / 2.0), Rotation3d())
            object_points += [
                wpiLibTranslationToOpenCV(corner_0.translation()),
                wpiLibTranslationToOpenCV(corner_1.translation()),
                wpiLibTranslationToOpenCV(corner_2.translation()),
                wpiLibTranslationToOpenCV(corner_3.translation())
            ]

            # Add image points from observation
            image_points += [
                [observation.corners[0][0][0], observation.corners[0][0][1]],
                [observation.corners[0][1][0], observation.corners[0][1][1]],
                [observation.corners[0][2][0], observation.corners[0][2][1]],
                [observation.corners[0][3][0], observation.corners[0][3][1]]
            ]

            # Add tag ID and pose
            tag_ids.append(observation.tagID)
            tag_poses.append(tag_pose)

    # Single tag, return two poses
    if len(tag_ids) == 1:
        object_points = np.array([[-tag_size / 2.0, tag_size / 2.0, 0.0],
                                  [tag_size / 2.0, tag_size / 2.0, 0.0],
                                  [tag_size / 2.0, -tag_size / 2.0, 0.0],
                                  [-tag_size / 2.0, -tag_size / 2.0, 0.0]])
        try:
            _, rvecs, tvecs, errors = cv2.solvePnPGeneric(object_points, np.array(image_points),
                                                          config.calibConfig.camera_matrix,
                                                          config.calibConfig.distortion_coefficients,
                                                          flags=cv2.SOLVEPNP_IPPE_SQUARE)
        except:
            return None

        # Calculate WPILib camera poses
        field_to_tag_pose = tag_poses[0]
        camera_to_tag_pose_0 = openCVPoseToWPILib(tvecs[0], rvecs[0])
        camera_to_tag_pose_1 = openCVPoseToWPILib(tvecs[1], rvecs[1])
        camera_to_tag_0 = Transform3d(camera_to_tag_pose_0.translation(), camera_to_tag_pose_0.rotation())
        camera_to_tag_1 = Transform3d(camera_to_tag_pose_1.translation(), camera_to_tag_pose_1.rotation())
        field_to_camera_0 = field_to_tag_pose.transformBy(camera_to_tag_0.inverse())
        field_to_camera_1 = field_to_tag_pose.transformBy(camera_to_tag_1.inverse())
        field_to_camera_pose_0 = Pose3d(field_to_camera_0.translation(), field_to_camera_0.rotation())
        field_to_camera_pose_1 = Pose3d(field_to_camera_1.translation(), field_to_camera_1.rotation())

        # Return result
        return Poses(field_to_camera_pose_0, field_to_camera_pose_1)

    # Multi-tag, return one pose
    else:
        # Run SolvePNP with all tags
        try:
            _, rvecs, tvecs, errors = cv2.solvePnPGeneric(np.array(object_points), np.array(image_points),
                                                          config.local_config.camera_matrix,
                                                          config.local_config.distortion_coefficients,
                                                          flags=cv2.SOLVEPNP_SQPNP)
        except:
            return None

        # Calculate WPILib camera pose
        camera_to_field_pose = openCVPoseToWPILib(tvecs[0], rvecs[0])
        camera_to_field = Transform3d(camera_to_field_pose.translation(), camera_to_field_pose.rotation())
        field_to_camera = camera_to_field.inverse()
        field_to_camera_pose = Pose3d(field_to_camera.translation(), field_to_camera.rotation())

        # Return result
        return Poses(field_to_camera_pose)
