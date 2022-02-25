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
from collections import namedtuple
from scipy.spacial import euclidean
from numba import njit

PET_NAME = ["PET"]
ANTERIOR_COMMISSURE_NAME = ["AC"]
LEFT_TRUE_CORD_NAMES = ["LC" + str(i) for i in range(1, 6)]
RIGHT_TRUE_CORD_NAMES = ["RC" + str(i) for i in range(1, 6)]
LEFT_FALSE_CORD_NAMES = ["LFC" + str(i) for i in range(1, 6)]
RIGHT_FALSE_CORD_NAMES = ["RFC" + str(i) for i in range(1, 6)]
MIDLINE_NAMES = ["ML" + str(i) for i in range(1, 3)]
RIGHT_ARYEPIGLOTTIS_NAMES = ["RAE" + str(i) for i in range(1, 3)]
LEFT_ARYEPIGLOTTIS_NAMES = ["LAE" + str(i) for i in range(1, 3)]
AnglesReturn = namedtuple(
    "AnglesReturn",
    ["true_angles", "true_angles_l", "true_angles_r", "midlines", "lines_r", "lines_r"],
)


def _set_ends(line: Line, cord: np.ndarray):
    c = cord[np.logical_not(np.isnan(cord).any(axis=1))]
    y = c[len(c) - 1, 1]
    if line.slope != 0:
        line.end2 = (int((y - line.intercept) / line.slope), int(y))
    else:
        line.end2 = (1, int(y))
    y = c[0][1]
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


@njit()
def angle_between_lines(slope0: np.float_, slope1: np.float_):
    return np.degrees(np.arctan(slope0.slope - slope1.slope) / (1 + slope0.slope * slope1.slope))


def _calc_lines_angles(
    midline_points: np.ndarray,
    comm: np.ndarray,
    true_points_l: np.ndarray,
    true_points_r: np.ndarray,
    false_points_l: np.ndarray,
    false_points_r: np.ndarray,
    aryepiglottis_points_r: np.ndarray,
    aryepiglottis_points_l: np.ndarray,
) -> ("np.ndarray", "np.ndarray", "np.ndarray", "np.ndarray", List[Line], List[Line]):
    """
    creates linear regression lines on a series of points and computes true_angles btween the 2 lines
    :param comm:
    :param true_points_r:
    :param true_points_l:
    :return: (angles_filtered, angels, true_angles_l, angle_r, lines_l, lines_r)
        true_angles np.ndarray:: The anterior glottic angle for each frame in degrees.
        true_angles_l np.ndarray: the angle of the lines_l cord for each frame in degrees.
        angle_r np.ndarray: the angle of the lines_r cord for each frame in degrees.
        lines_l: the line of the left cord edge
        lines_r: the line of the right cord edge.
    """
    comm_3d = comm.reshape((1, comm.shape[0], comm.shape[1]))
    midline_points = np.concatenate((comm_3d, midline_points), axis=0)
    true_points_r = np.concatenate((comm_3d, true_points_r), axis=0)
    true_points_l = np.concatenate((comm_3d, true_points_l), axis=0)
    true_angles = np.empty(shape=comm.shape[0], dtype=np.float_)
    true_angles_l = np.empty(shape=comm.shape[0], dtype=np.float_)
    true_angles_r = np.empty(shape=comm.shape[0], dtype=np.float_)
    true_angles[:] = np.nan
    true_angles_l[:] = np.nan
    true_angles_r[:] = np.nan
    lines_l = [None] * comm.shape[0]
    lines_r = [None] * comm.shape[0]
    midlines = [None] * comm.shape[0]
    comms_there = np.logical_not(np.isnan(comm).any(axis=1))
    # a list of booleans for each commisure point that is true if either coordinate in the point is nan
    for i in range(comm.shape[0]):
        # checks if there are less than 3 points in left_points[:,i] and left_points[:, i] with no nan coordinate
        midline_points_f = midline_points[
            np.logical_not(np.isnan(midline_points[:, i]).any(axis=2)), i
        ]
        if midline_points.shape[0] > 3:
            midlines[i] = regression_line(midline_points_f)
        left_points_f = true_points_l[np.logical_not(np.isnan(true_points_l[:, i]).any(axis=1)), i]
        right_points_f = true_points_r[np.logical_not(np.isnan(true_points_r[:, i]).any(axis=1)), i]
        if left_points_f.shape[0] >= 3 and right_points_f.shape[0] >= 3:
            lines_l[i] = cord_line(left_points_f, comms_there[i])
            lines_r[i] = cord_line(right_points_f, comms_there[i])
            if lines_l[i] is None or lines_r[i] is None:
                return np.nan, np.nan, None, None
            _set_ends(lines_l[i], left_points_f)
            _set_ends(lines_r[i], right_points_f)
            if lines_r[i].slope < 0 < lines_l[i].slope:
                return np.nan, np.nan, None, None
            true_angles[i] = angle_between_lines(lines_l[i].slope, lines_r[i].slope)
            if not midlines[i] is None:
                # calculate left and right angles
                true_angles_l[i] = angle_between_lines(lines_l[i].slope, midlines[i].slope)
                true_angles_r = true_angles[i] - true_angles_l[i]
                true_angles_r[i] = -(true_angles[i] - true_angles_l[i])
    return true_angles, true_angles_l, true_angles_r, lines_l, lines_r, midlines


class Analysis(dga.Analysis):
    def __init__(self, h5_path: str, dlc_scorer: str, video_path: str):
        h5_path = os.path.abspath(h5_path)
        if not os.path.isfile(h5_path):
            raise FileNotFoundError(h5_path)
        dga.Analysis.__init__(self, h5_path, dlc_scorer)
        self.video_path = video_path
        self.out_file = None
        midline_points = np.squeeze(dga.utils.point_array(self.df, MIDLINE_NAMES))
        right_true_points = np.squeeze(dga.utils.point_array(self.df, RIGHT_TRUE_CORD_NAMES))
        left_true_points = np.squeeze(dga.utils.point_array(self.df, LEFT_TRUE_CORD_NAMES))
        right_false_points = np.squeeze(dga.utils.point_array(self.df, RIGHT_FALSE_CORD_NAMES))
        left_false_points = np.squeeze(dga.utils.point_array(self.df, LEFT_FALSE_CORD_NAMES))
        right_aeglottis_points = np.squeeze(
            dga.utils.point_array(self.df, RIGHT_ARYEPIGLOTTIS_NAMES)
        )
        left_aeglottis_points = np.squeeze(dga.utils.point_array(self.df, LEFT_ARYEPIGLOTTIS_NAMES))
        commissure = np.squeeze(dga.utils.point_array(self.df, ANTERIOR_COMMISSURE_NAME))
        (
            self.angles_filtered,
            self.angles,
            self.angles_l,
            self.angles_r,
            self.left,
            self.right,
        ) = _calc_lines_angles(commissure, right_true_points, left_true_points)
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


def cord_line(points, comm) -> (Line, None):
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
    if pf.rvalue ** 2 < 0.9:
        pfc = outlier_del(pfx, pfy, comm, pf)
        if abs(pfc.rvalue) > abs(pf.rvalue):
            pf = pfc
    if pf.rvalue ** 2 < 0.8:
        return
    return Line(slope=pf.slope, intercept=pf.intercept)


def regression_line(points: np.ndarray, min_r2=0.9) -> Line:
    linreg = stats.linregress(points)
    if linreg.rvalue ** 2 > min_r2:
        return Line(slope=linreg.slope, intercept=linreg.intercept)


def outlier_del(pfx, pfy, comm, pf):
    """Deletes outliers from sufficiently large cord lists."""
    if comm:
        pfx = pfx[1:]
        pfy = pfy[1:]
    if len(pfx) > 3:
        for i in range(len(pfx) - 1):
            newx = pfx[:-1]
            newy = pfy[:-1]
            newline = stats.linregress(newx, newy)
            if len(newx) > 3:
                newline = outlier_del(newx, newy, False, newline)
            if newline[2] > pf[2]:
                pf = newline
    return pf
