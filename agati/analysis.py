import csv
import os
import typing
import cv2
import dlc_generic_analysis as dga
import numpy as np
from scipy import stats
from draw import draw
from dlc_generic_analysis.geometries import Line
from matplotlib import pyplot as plt
from tqdm import tqdm
from typing import List

COMMISSURE_NAME = ["AC"]
LEFT_NAMES = ["LC1", "LC2", "LC3", "LC4", "LC5", "LVP"]
RIGHT_NAMES = ["RC1", "RC2", "RC3", "RC4", "RC5", "RVP"]


def _set_ends(line: Line, cord: np.ndarray):
    y = cord[len(cord) - 1, 1]
    if line.slope != 0:
        line.end2 = (int((y - line.intercept) / line.slope), int(y))
    else:
        line.end2 = (1, int(y))
    y = cord[0, 1]
    if line.slope != 0:
        line.end1 = (int((y - line.intercept) / line.slope), int(y))
    else:
        line.end1 = (1, int(y))
    return line


def analyze(video_paths: [str], model_dir: str):
    h5s, dlc_scorer = dga.dlc_analyze(model_dir, video_paths)
    h5s = dga.filter.threshold_confidence(h5s, 0.85)
    for i in range(len(h5s)):
        analysis = Analysis(h5s[i], dlc_scorer, video_paths[i])
        analysis.write_csv()
        analysis.draw()
        analysis.plot()


def calc_glottic_angle(
    left_cord, right_cord, comm_there
) -> typing.Tuple[np.float64, np.float64, Line, Line]:
    """
    Alternative anterior glottic angle of opening calculation.
    :param left_cord: the points the left vocal cord
    :param right_cord: the points onn the right vocal cord
    :param comm_there: # if there is a comm in the left_cord and right_cord lists
    :return: (angle, left_angle, left, right)
        angle: the angle between the 2 cords in degrees
        left_angle: the angle of the left chord
        left_line: the line representing the edge of the left chord
        right_line: the line representing the edge of the right chord
    """
    left_cord = left_cord[np.logical_not(np.isnan(left_cord)).any(axis=1)]
    right_cord = right_cord[np.logical_not(np.isnan(right_cord)).any(axis=1)]
    left_line = calc_reg_line(left_cord, comm_there)
    right_line = calc_reg_line(right_cord, comm_there)
    if left_line is None or right_line is None:
        return np.nan, np.nan, left_line, right_line
    left_line = _set_ends(left_line, left_cord)
    right_line = _set_ends(right_line, right_cord)
    if right_line.slope < 0 < left_line.slope:
        return np.nan, np.nan, None, None
    angle = np.arctan(
        abs((left_line.slope - right_line.slope) / (1 + left_line.slope * right_line.slope))
    )
    # Angles of cords from vertical midline
    left_mid_x = left_line.end2[0] - left_line.end1[0]
    left_mid_y = abs(left_line.end2[1] - left_line.end1[1])
    if left_mid_x == 0:
        left_mid_x = 0.00001
    angle_l = np.degrees(np.arctan(left_mid_y / left_mid_x))
    if left_line.slope < 0:
        left_angle = 90 - angle_l
    else:
        left_angle = -angle_l - 90
    return angle, left_angle, left_line, right_line


def _calc_lines_angles(
    comm: np.ndarray, right_points: np.ndarray, left_points: np.ndarray
) -> ("np.ndarray", "np.ndarray", "np.ndarray", "np.ndarray", List[Line], List[Line]):
    """
    creates linear regression lines on a series of points and computes angles btween the 2 lines
    :param comm:
    :param right_points:
    :param left_points:
    :return: (angles_filtered, angels, angles_l, angle_r, line_l, line_r)
        angles_filtered np.ndarray: anterior glottic angle with nan vales removed
        angles np.ndarray:: The anterior glottic angle for each frame in degrees.
        angles_l np.ndarray: the angle of the line_l cord for each frame in degrees.
        angle_r np.ndarray: the angle of the line_r cord for each frame in degrees.
        line_l: the line of the left cord edge
        line_r: the line of the right cord edge.
    """
    print(right_points.shape)
    comm_3d = comm.reshape((1, comm.shape[0], comm.shape[1]))
    right_points = np.concatenate((comm_3d, right_points), axis=0)
    left_points = np.concatenate((comm_3d, left_points), axis=0)
    angles = np.zeros(shape=comm.shape[0], dtype=np.float_)
    angles_l = angles
    angles_r = angles
    line_l = []
    line_r = []
    comm_there = np.logical_not(
        np.isnan(comm).any(axis=1)
    )  # a list of booleans for each commisure point that is true
    # if either coordinate in the point is nan
    for i in range(comm.shape[0]):
        cords_there = True
        if right_points[np.logical_not(np.isnan(right_points[:, i]).any(axis=1)), i].shape[0] < 3:
            # checks if there are less than 3 points in right_points[:, i] with no nan coordinate
            cords_there = False
        if left_points[np.logical_not(np.isnan(left_points[:, i]).any(axis=1)), i].shape[0] < 3:
            # checks if there are less than 3 points in left_points[:, i] with no nan coordinate
            cords_there = False
        if cords_there:
            angles[i], angles_l[i], curr_line_l, curr_line_r = calc_glottic_angle(
                left_points[:, i], right_points[:, i], comm_there[i]
            )

            line_l.append(curr_line_l)
            line_r.append(curr_line_r)
            if not np.isnan(angles_l[i]):
                angles_r[i] = -(angles[i] - angles_l[i])
            else:
                angles_r[i] = np.nan
        else:
            line_l.append(None)
            line_r.append(None)
            angles[i] = np.nan
            angles_l[i] = np.nan
            angles_r[i] = np.nan
            line_l[i] = None
            line_r[i] = None
        print(
            f"angle {round(angles[i], 3)}, left angle {round(angles_l[i], 3)}, right angle {round(angles_r[i], 3)}\n"
        )
    angles_filered = angles[np.logical_not(np.isnan(angles))]
    return angles_filered, angles, angles_l, angles_r, line_l, line_r


class Analysis(dga.Analysis):
    def __init__(self, h5_path: str, dlc_scorer: str, video_path: str):
        h5_path = os.path.abspath(h5_path)
        if not os.path.isfile(h5_path):
            raise FileNotFoundError(h5_path)
        dga.Analysis.__init__(self, h5_path, dlc_scorer)
        self.video_path = video_path
        self.out_file = None
        right_points = np.squeeze(dga.utils.point_array(self.df, RIGHT_NAMES))
        left_points = np.squeeze(dga.utils.point_array(self.df, LEFT_NAMES))
        commissure = np.squeeze(dga.utils.point_array(self.df, COMMISSURE_NAME))
        # for i in range(right_points.shape[0]):
        (
            self.angles_filtered,
            self.angles,
            self.angles_l,
            self.angles_r,
            self.left,
            self.right,
        ) = _calc_lines_angles(commissure, right_points, left_points)
        # WTF is this doing
        display_angles = []
        count = 0
        percentile_97 = np.percentile(self.angles_filtered, 97)
        for i in range(self.angles.shape[0]):
            if np.isnan(self.angles[i]):
                display_angles.append(np.nan)
            elif count >= self.angles_filtered.shape[0]:
                display_angles.append(np.nan)
            elif self.angles[i] > percentile_97:
                display_angles.append(0)
                count += 1
            else:
                display_angles.append(self.angles_filtered[count])
                count += 1
        self.angles_transformed = self.angles
        self.display_angles = np.array(display_angles)
        vid = cv2.VideoCapture(self.video_path)
        frame_rate = vid.get(cv2.CAP_PROP_FPS)
        # compute cord velocities in degrees / second
        self.velocities = np.zeros(shape=self.angles_transformed.shape[0])
        self.velocities[0] = np.nan
        print("computing velocities")
        for i in tqdm(range(1, self.angles_transformed.shape[0] - 1)):
            if not np.isnan(self.angles_transformed[i]) and np.isnan(
                self.angles_transformed[i + 1]
            ):
                self.velocities[i] = (
                    self.angles_transformed[i + 1] - self.angles_transformed[i]
                ) * frame_rate
            else:
                self.velocities[i] = np.nan
        # compute accelerations in degrees / second^2
        self.accelerations = np.zeros(shape=self.angles_transformed.shape[0])
        self.accelerations[0] = np.nan
        print("computing accelerations")
        for i in tqdm(range(1, self.velocities.shape[0])):
            if not np.isnan(self.velocities[i]) and not np.isnan(self.velocities[i - 1]):
                self.accelerations[i] = self.velocities[i] - self.velocities[i - 1]

    def draw(self, outfile: str = None):
        self.out_file = draw(self.video_path, self.left, self.right, self.angles, outfile)

    def write_csv(self, file_path: str = None):
        if file_path is None:
            if self.out_file is not None:
                file_path = os.path.splitext(self.out_file)[0] + ".csv"
            else:
                file_path = os.path.splitext(self.video_path)[0] + "_analyzed.csv"
            with open(file_path, "w") as file:
                writer = csv.writer(file, delimiter=",")
                writer.writerow(
                    [
                        "Frame Number",
                        "Anterior Glottic Angle",
                        "Angle of Left Cord",
                        "Angle of Right Cord",
                    ]
                )
                for i in range(len(self.angles)):
                    writer.writerow([i + 1, self.angles[i], self.angles_l[i], self.angles_r[i]])

    def plot(self, file_path=None):
        if file_path is None:
            if self.out_file is not None:
                file_path = os.path.splitext(self.out_file)[0] + "_graph.png"
            else:
                file_path = os.path.splitext(self.video_path)[0] + "_analyzed.csv"
        plt.figure()
        plt.title("Glottic Angle")
        plt.plot(self.display_angles)
        plt.xlabel("Frames")
        plt.ylabel("Angle Between Cords")
        plt.savefig(file_path)


def calc_reg_line(points, comm) -> (Line, None):
    """
    Given a list corresponding to points plotted on a vocal cord. Calculates
    a regression line from those points which is used to represent the cord.
    :param points: the points to use to create the line
    :param comm: the commissure point
    :return: if a line representing the edge of a vocal cord.
    """
    pfx = points[:, 0]
    pfy = points[:, 1]
    pf = stats.linregress(pfx, pfy)
    if comm and len(pfx) > 3:
        pfc = stats.linregress(pfx[1:], pfy[1:])
        if abs(pfc.rvalue) > abs(pf.rvalue):
            pf = pfc
    if pf.rvalue**2 < 0.8:
        return None
    return Line(slope=pf.slope, intercept=pf.intercept)
