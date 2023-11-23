import math

import open3d as o3d
import copy
import numpy as np
import matplotlib.pyplot as plt
import scipy
from landmark_ids import *
from enum import Enum
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from get_pipe_data import get_pipe_data


def create_pc_from_point_array(x, y, z):
    if len(x.shape) == 1:
        ref_coords = np.concatenate([np.reshape(x, (-1, 1)),
                                     np.reshape(y, (-1, 1)),
                                     np.reshape(z, (-1, 1))], axis=1)
    else:
        ref_coords = (
            np.array([np.reshape(x, (-1, 1)),
                      np.reshape(y, (-1, 1)),
                      np.reshape(z, (-1, 1))])).squeeze().transpose()

    plane_pc = o3d.geometry.PointCloud()
    plane_pc.points = o3d.utility.Vector3dVector(ref_coords)
    plane_pc.estimate_normals()
    # _, ids = plane_pc.remove_statistical_outlier(16, 6)

    # if len(ref_coords) != len(ids):
    #     warn_txt = f"{len(ref_coords) - len(ids)} points have been removed as outliers"
    #     warnings.warn(warn_txt, Warning)

    return plane_pc


def align_points_to_axis_plane(points, axis="yz"):
    # Create axis plane
    values = np.linspace(-0.5, 0.5, 21)
    # specifies the range for the non zero values
    val_range_1, val_range_2 = np.meshgrid(values, values)
    val_zeros = np.zeros((len(values), len(values)))

    if axis == "yz":
        order = [2, 1, 0]
        fit_ids, pred_idx = [1, 2], 0

    elif axis == "xz":
        order = [1, 0, 2]
        fit_ids, pred_idx = [0, 2], 1

    # defaults to xy
    else:
        order = [0, 1, 2]
        fit_ids, pred_idx = [1, 0], 2

    axis_plane_vals = np.array([val_range_1, val_range_2, val_zeros])
    axis_plane_vals = axis_plane_vals[order]
    axis_plane_pc = create_pc_from_point_array(*axis_plane_vals)

    # Fist plane to points
    A = np.hstack((points[:, fit_ids], np.ones((len(points), 1))))
    b = points[:, pred_idx]

    res = scipy.optimize.lsq_linear(A, b, max_iter=1000)
    val_sym = res.x[0] * axis_plane_vals[1] + res.x[1] * axis_plane_vals[2] + res.x[2]
    point_plane_vals = np.array([val_range_1, val_range_2, val_sym])
    point_plane_vals = point_plane_vals[order]
    point_plane_pc = create_pc_from_point_array(*point_plane_vals)

    #
    _, tform = fit_point_to_plane(point_plane_pc, axis_plane_pc)

    return tform, axis_plane_vals, point_plane_vals


def fit_point_to_plane(moving, fixed, threshold=0.02, tform_init=np.identity(4)):
    reg_p2l = o3d.pipelines.registration.registration_icp(
        moving, fixed, threshold, tform_init,
        o3d.pipelines.registration.TransformationEstimationPointToPlane())

    source_temp = copy.deepcopy(moving)
    source_temp.transform(reg_p2l.transformation)

    return source_temp, reg_p2l.transformation


def get_poly_values(x, c):
    A = np.concatenate([np.power(x, p) for p in range(len(c) - 1, -1, -1)], axis=1)
    y = np.matmul(A, np.reshape(c, (-1, 1)))
    return y


class ViewAngle(Enum):
    home = [45, -45, 0]
    default = [65, -135 + 45 * 8, 0]
    XY = [90, -90, 0]
    YZ = [0, 0, 0]


class KeyPoints:
    def __init__(self, xyz):
        self.all, self.sym_line, self.mouth, self.eyes = None, None, None, None
        self.eyebrows, self.cheeks, self.left_eye, self.right_eye = None, None, None, None
        self.left_eyebrow, self.right_eyebrow, self.left_cheek, self.right_cheek = None, None, None, None

        self.y_plane, self.x_plane, self.nose_tip = None, None, None

        self.point_dict = None

        self.update_values(xyz)

    def update_values(self, xyz):
        self.all = xyz[np.array(keypointIDs) - 1, :]
        self.sym_line = xyz[np.array(symLineIDs) - 1, :]
        self.mouth = xyz[np.array(mouthIDs) - 1, :]
        self.eyes = xyz[np.array(eyeIDs) - 1, :]
        self.eyebrows = xyz[np.array(eyebrowIDs) - 1, :]
        self.cheeks = xyz[np.array(cheekIDs) - 1, :]
        self.left_eye = xyz[np.array(leftEyeIDs) - 1, :]
        self.right_eye = xyz[np.array(rightEyeIDs) - 1, :]
        self.left_eyebrow = xyz[np.array(leftEyebrowIDs) - 1, :]
        self.right_eyebrow = xyz[np.array(rightEyebrowIDs) - 1, :]
        self.left_cheek = xyz[np.array(leftCheekIDs) - 1, :]
        self.right_cheek = xyz[np.array(rightCheekIDs) - 1, :]

        self.x_plane = xyz[0, :]
        self.y_plane = xyz[[6, 64, 294], :]
        self.nose_tip = xyz[4, :]

        self.point_dict = {"Mouth": self.mouth, "Eyes": self.eyes,
                           "Brows": self.eyebrows, "Cheeks": self.cheeks}


class FaceCloud:
    def __init__(self, xyz):
        # all arrays are Yx3 numpy arrays.
        xyz *= -1
        self.points: np.ndarray = xyz
        self.key_points = KeyPoints(xyz)
        self.shape_feature = None
        self.delta_feature = None
        self.fusion_feature = None

    def update_points(self):
        self.key_points = KeyPoints(self.points)

    def centre_nose_tip(self):
        delta = (np.array([0, 0, 0]) - self.key_points.nose_tip)
        self.points += delta
        self.key_points = KeyPoints(self.points)

    def scale_face(self):
        x_width = max(self.points[:, 0]) - min(self.points[:, 0])
        y_width = max(self.points[:, 1]) - min(self.points[:, 1])
        self.points[:, 0] *= (1 / x_width)
        self.points[:, 1] *= (1 / y_width)
        self.points[:, 2] *= (2 / (x_width + y_width))
        self.key_points = KeyPoints(self.points)

    def preprocess(self):
        self.centre_nose_tip()
        self.align_face()
        self.centre_nose_tip()
        # self.scale_face()

    def align_face(self, demo=False):
        # align to yz axis
        tform, axis_plane_v, point_plane_v = align_points_to_axis_plane(self.key_points.sym_line, "yz")

        face_pc = create_pc_from_point_array(self.points[:, 0], self.points[:, 1], self.points[:, 2])
        face_pc.transform(tform)

        self.points = np.asarray(face_pc.points)
        self.update_points()

        # align to yz axis
        tform, axis_plane_h, point_plane = align_points_to_axis_plane(self.key_points.y_plane, "xy")

        face_pc = create_pc_from_point_array(self.points[:, 0], self.points[:, 1], self.points[:, 2])
        face_pc.transform(tform)

        self.points = np.asarray(face_pc.points)
        self.update_points()

        # add face points
        if demo:
            fig = plt.figure()
            ax = fig.add_subplot(projection='3d')

            ax.scatter(self.points[:, 0], self.points[:, 1], self.points[:, 2], marker="*", s=5)
            ax.scatter(self.key_points.sym_line[:, 0], self.key_points.sym_line[:, 1], self.key_points.sym_line[:, 2],
                       marker="+", color=[0, 1, 0], s=20)
            # add YZ plane
            ax.plot_surface(*axis_plane_h, alpha=0.2, color=[0, 1, 0])
            # ax.plot_surface(*point_plane_v, alpha=0.2, color=[1, 0, 0])

            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')

            # XY view
            ax.view_init(*ViewAngle.YZ.value)

            plt.show()

    def create_shape_feature(self, demo=False):
        """
        Creates a feature vector based on the shapes of curves on the XY plane of the face

        :param demo: controls the visual output of the function
        :return: Vector of length 49
        """

        mouth_ids = [range(6), range(5, 11), range(3, 8), np.append(0, np.array(range(19, 9, -1))),
                     range(20, 31), np.append(20, np.array(range(39, 29, -1)))]
        mouth_lines = [self.key_points.mouth[ids, :] for ids in mouth_ids]
        mouth_orders = [3, 3, 4, 3, 2, 2]

        eye_ids = [range(9), np.append(0, np.array(range(15, 7, -1)))]
        left_eye_lines = [self.key_points.left_eye[ids, :] for ids in eye_ids]
        right_eye_lines = [self.key_points.right_eye[ids, :] for ids in eye_ids]
        eye_lines = left_eye_lines + right_eye_lines
        eye_orders = [2, 2, 2, 2]

        eyebrow_ids = [[0, 2, 3, 6, 8], [1, 4, 5, 7]]
        left_eyebrow_lines = [self.key_points.left_eyebrow[ids, :] for ids in eyebrow_ids]
        right_eyebrow_lines = [self.key_points.right_eyebrow[ids, :] for ids in eyebrow_ids]
        eyebrow_lines = left_eyebrow_lines + right_eyebrow_lines
        eyebrow_orders = [2, 2, 2, 2]

        orders = mouth_orders + eye_orders + eyebrow_orders
        lines = mouth_lines + eye_lines + eyebrow_lines
        shape_values = [np.polyfit(line[:, 0], line[:, 1], order) for order, line in zip(orders, lines)]

        aspect_ratio_left = ((np.linalg.norm(self.key_points.left_eye[6, :] - self.key_points.left_eye[10, :]) +
                              np.linalg.norm(self.key_points.left_eye[3, :] - self.key_points.left_eye[15, :])) /
                             (2 * np.linalg.norm(self.key_points.left_eye[8, :] - self.key_points.left_eye[0, :])))

        aspect_ratio_right = ((np.linalg.norm(self.key_points.right_eye[6, :] - self.key_points.right_eye[10, :]) +
                               np.linalg.norm(self.key_points.right_eye[3, :] - self.key_points.right_eye[15, :])) /
                              (2 * np.linalg.norm(self.key_points.right_eye[8, :] - self.key_points.right_eye[0, :])))

        # shape_values = shape_values.append(aspect_ratio_left)

        shape_feature = np.concatenate(shape_values, axis=0)
        self.shape_feature = np.append(shape_feature, [aspect_ratio_left, aspect_ratio_right])

        if demo:
            fig = plt.figure()
            # gs = fig.add_gridspec(2, 2)
            # ax1 = fig.add_subplot(2, 2, 1)
            # colours = ["r", "r", "g", "g", "b", "b"]
            # for idx, (line, val) in enumerate(zip(mouth_lines, mouth_values)):
            #     x = np.reshape(np.linspace(min(line[:, 0]), max(line[:, 0]), 21), (-1, 1))
            #     y = get_poly_values(x, val)
            #     ax1.scatter(line[:, 0], line[:, 1], marker="*")
            #     ax1.plot(x, y, colours[idx])
            #
            # ax2 = fig.add_subplot(2, 2, 2)
            #
            # colours = ["r", "b", "r", "b"]
            # for idx, (line, val) in enumerate(zip(eye_lines, eye_values)):
            #     x = np.reshape(np.linspace(min(line[:, 0]), max(line[:, 0]), 21), (-1, 1))
            #     y = get_poly_values(x, val)
            #     ax2.scatter(line[:, 0], line[:, 1], marker="*")
            #     ax2.plot(x, y, colours[idx])
            #
            # ax3 = fig.add_subplot(2, 2, 3)
            # # ax3.scatter(self.key_points.right_eyebrow[[0, 2, 3, 6, 8], 0], self.key_points.right_eyebrow[[0, 2, 3, 6, 8], 1])
            # colours = ["r", "b", "r", "b"]
            # for idx, (line, val) in enumerate(zip(eyebrow_lines, eyebrow_values)):
            #     x = np.reshape(np.linspace(min(line[:, 0]), max(line[:, 0]), 21), (-1, 1))
            #     y = get_poly_values(x, val)
            #     ax3.scatter(line[:, 0], line[:, 1], marker="*")
            #     ax3.plot(x, y, colours[idx])

            ax4 = fig.add_subplot()
            colours = ["g", "g", "g", "g", "b", "b"] + ["r", "r", "r", "r"] + ["b", "b", "b", "b"]
            extend = 0.01
            for idx, (line, val) in enumerate(zip(lines, shape_values)):
                x = np.reshape(np.linspace(min(line[:, 0]) - extend, max(line[:, 0]) + extend, 21), (-1, 1))
                y = get_poly_values(x, val)
                # ax4.scatter(line[:, 0], line[:, 1], marker="*")
                ax4.plot(x, y, colours[idx])

            plt.show()

        return self.shape_feature

    def detect_action_units(self):
        # Mouth action units
        thresh, tol = 0.01, 0.003
        mouth_center = np.mean(self.key_points.mouth, axis=0)
        delta = self.key_points.mouth[[0, 10], 1] - mouth_center[1]
        AU12_v = np.any(delta >= thresh) and np.all(delta > -tol)
        print(AU12_v)

    def detect_action_units_legacy(self, neutral):
        def check_activation_y(region, ids, direction="Increase", thresh=0, tol=0.0):
            # has the landmark moved up or down?
            self_points = self.key_points.point_dict[region]
            ref_points = neutral.key_points.point_dict[region]

            delta = self_points[ids, 1] > ref_points[ids, 1]
            if direction == "Increase":
                return np.any(delta >= thresh) and np.all(delta > -tol)
            else:
                return np.any(delta <= -thresh) and np.all(delta < tol)

        def check_activation_x(region, left_ids, right_ids, direction="Increase", thresh=0, tol=0.0):
            self_points = self.key_points.point_dict[region]
            ref_points = neutral.key_points.point_dict[region]

            delta_left = self_points[left_ids, 0] - ref_points[left_ids, :]
            delta_right = self_points[right_ids, 0] - ref_points[right_ids, :]

            if direction == "Increase":
                left_activation = np.any(delta_left <= -thresh) and np.all(delta_left < tol)
                right_activation = np.any(delta_right >= thresh) and np.all(delta_right > -tol)
                return left_activation and right_activation
            else:
                left_activation = np.any(delta_left >= thresh) and np.all(delta_left > tol)
                right_activation = np.any(delta_right <= -thresh) and np.all(delta_right < -tol)
                return left_activation and right_activation

        mouth_corners_self = self.key_points.mouth[[0, 10], :]
        mouth_corners_ref = neutral.key_points.mouth[[0, 10], :]

        AU12_a = check_activation_y("Mouth", [0, 10], tol=0.01)
        AU12_b = check_activation_x("Mouth", [10], [0], tol=0.01)
        AU12 = AU12_a and AU12_b
        return np.array([AU12])

    def create_delta_feature(self, reference, demo=False):
        def create_local_features(ref_points, self_points, subset=None):
            flag = False

            if not subset:
                point_count = self_points.shape[0]
            else:
                point_count = len(subset)

            # center of local region
            c_ref = np.mean(ref_points, axis=0)
            c_self = np.mean(self_points, axis=0)

            c_delta = c_ref - c_self
            ref_points_subset = ref_points[subset, :]
            self_points = self_points[subset, :] + c_delta

            reference_distances = ref_points_subset - c_ref
            self_distances = self_points - c_ref

            relative_movement = self_points - ref_points_subset

            if np.any(abs(relative_movement) > 15):
                flag = True

            ref_dist_mag = np.sqrt(np.sum(np.power(reference_distances, 2), axis=1))
            self_dist_mag = np.sqrt(np.sum(np.power(self_distances, 2), axis=1))
            # change in distance from the center of the region
            center_delta_mag = self_dist_mag - ref_dist_mag

            direction = np.sign(center_delta_mag)

            movement_mag = np.sqrt(np.sum(np.power(relative_movement, 2), axis=1))

            angle_cxy = np.reshape(
                np.array([math.atan2(self_distances[idx, 1], self_distances[idx, 0]) for idx in range(point_count)]) -
                np.array([math.atan2(reference_distances[idx, 1], reference_distances[idx, 0]) for idx in
                          range(point_count)]), (-1, 1))
            angle_cxz = np.reshape(
                np.array([math.atan2(self_distances[idx, 2], self_distances[idx, 0]) for idx in range(point_count)]) -
                np.array([math.atan2(reference_distances[idx, 2], reference_distances[idx, 0]) for idx in
                          range(point_count)]), (-1, 1))
            angle_cyz = np.reshape(
                np.array([math.atan2(self_distances[idx, 2], self_distances[idx, 1]) for idx in range(point_count)]) -
                np.array([math.atan2(reference_distances[idx, 2], reference_distances[idx, 1]) for idx in
                          range(point_count)]), (-1, 1))

            angles_c = np.concatenate([angle_cxy, angle_cxz, angle_cyz], axis=1)

            sub_feature = np.concatenate([
                relative_movement,
                np.expand_dims(center_delta_mag, axis=1),
                np.expand_dims(movement_mag, axis=1),
                np.expand_dims(direction, axis=1),
                angles_c], axis=1).flatten()

            display_vals = {"norm_points": self_points,
                            "ref_points": ref_points,
                            "size": 20 * (movement_mag / min(movement_mag)),
                            "direction": direction,
                            "center": c_ref}

            return sub_feature, display_vals, flag

        eye_ids = [4, 8, 12]
        mouth_ids = [0, 3, 5, 7, 10, 13, 17, 23, 27, 33, 37]
        brow_ids = [0, 1, 3, 7, 8]
        left_eye_vals, left_eye_draw, flag = create_local_features(
            reference.key_points.left_eye,
            self.key_points.left_eye,
            eye_ids
        )
        right_eye_vals, right_eye_draw, flag = create_local_features(
            reference.key_points.right_eye,
            self.key_points.right_eye,
            eye_ids
        )
        mouth_vals, mouth_draw, flag = create_local_features(
            reference.key_points.mouth,
            self.key_points.mouth,
            mouth_ids
        )
        left_brow_vals, l_b_mag, flag = create_local_features(
            reference.key_points.left_eyebrow,
            self.key_points.left_eyebrow,
            brow_ids
        )
        right_brow_vals, r_b_mag, flag = create_local_features(
            reference.key_points.right_eyebrow,
            self.key_points.right_eyebrow, brow_ids
        )

        delta_feature = np.concatenate(
            [left_eye_vals, right_eye_vals, mouth_vals,
                    left_brow_vals, right_brow_vals], axis=0)
        self.delta_feature = delta_feature

        if demo:
            draw_utils = [right_eye_draw, left_eye_draw, mouth_draw]
            print(right_eye_draw["size"], right_eye_draw["direction"])
            f, axs = plt.subplots(2, 2)
            gs = f.add_gridspec(2, 2)
            axs[1, 0] = f.add_subplot(gs[1, :])
            for idx, region in enumerate(draw_utils):
                ax = axs[math.floor(idx / 2), idx % 2]
                colour = [["r", "g"][direction > 0] for direction in region["direction"]]

                ax.scatter(region["center"][0], region["center"][1], s=50, marker="+")
                ax.scatter(region["norm_points"][:, 0], region["norm_points"][:, 1],
                           s=region["size"], marker="o", c=colour)
                ax.scatter(region["ref_points"][:, 0], region["ref_points"][:, 1],
                           s=15, marker="o", c="#6666FF")

            # axs[0, 0].scatter(reference.key_points.left_eye[:, 0], reference.key_points.left_eye[:, 1], marker="*", c="b")
            # axs[0, 1].scatter(reference.key_points.right_eye[:, 0], reference.key_points.right_eye[:, 1], marker="*",
            #                   c="b")

            # ax_2 = fig.add_subplot(2, 1, 2)
            # colour = [["r", "g"][direction > 0] for direction in mouth_draw["direction"]]
            #
            # ax_2.scatter(mouth_draw["center"][0], mouth_draw["center"][1], s=50, marker="+")
            # ax_2.scatter(mouth_draw["norm_points"][:, 0], mouth_draw["norm_points"][:, 1],
            #              s=mouth_draw["size"], marker="o", c=colour)
            # ax_2.scatter(reference.key_points.mouth[:, 0], reference.key_points.mouth[:, 1], marker="*", c="b")
            # # ax.scatter(self.key_points.all[:, 0], self.key_points.all[:, 1], marker="+")
        return delta_feature

    def render(self, view=ViewAngle.home):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(self.points[:, 0], self.points[:, 1], self.points[:, 2], marker="*")

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        ax.view_init(*view.value)

        plt.show()


base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task')
options = vision.FaceLandmarkerOptions(base_options=base_options, output_face_blendshapes=True,
                                       output_facial_transformation_matrixes=True, num_faces=1, )
detector = vision.FaceLandmarker.create_from_options(options)

im_path = "sample_images/Ben_Face.png"
# get image as RGB array
img_array = cv2.cvtColor(cv2.imread(im_path), cv2.COLOR_BGR2RGB)
# get image as mediapipe image
img_mp = mp.Image(data=img_array, image_format=mp.ImageFormat.SRGB)
face_landmarks, blend_data, _ = get_pipe_data(detector, img_mp)

face = FaceCloud(face_landmarks)
face.preprocess()
face.detect_action_units()