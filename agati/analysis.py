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

line = np.dtype(
    [("slope", "float64"), ("intercept", "float64"), ("end0", "float64", 2), ("end1", "float64", 2)]
)


def slope_line(slope, intercept):
    return np.array((slope, intercept, [0, intercept], [1, int(intercept + slope)]), dtype=line)


@njit()
def points_line(end0, end1):
    if not end1[0] == end0[0]:
        slope = (end1[1] - end0[1]) / (end1[0] - end0[0])
    else:
        slope = 9e9
    return np.array((slope, end0[1] - slope * end0[0], end0, end1), dtype=line)


@njit
def _set_ends(line: np.ndarray, cord: np.ndarray):
    c = cord[np.logical_not(np.isnan(cord).any(axis=1))]
    y = c[len(c) - 1, 1]
    if line.slope != 0:
        line["end1"] = [int((y - line["intercept"]) / line["slope"]), int(y)]
    else:
        line["end1"] = (1, int(y))
    y = c[0][1]
    if line["slope"] != 0:
        line["end0"] = (int((y - line["intercept"]) / line["slope"]), int(y))
    else:
        line["end0"] = (1, int(y))
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
    return np.degrees(np.arctan(slope0 - slope1) / (1 + slope0 * slope1))


def create_lines(
    midline_points: np.ndarray,
    commissure: np.ndarray,
    true_points_l: np.ndarray,
    true_points_r: np.ndarray,
    false_points_l: np.ndarray,
    false_points_r: np.ndarray,
    aryepiglottis_points_l: np.ndarray,
    aryepiglottis_points_r: np.ndarray,
) -> (List[Line], List[Line], List[Line], List[Line], List[Line], List[Line], List[Line]):
    """
    Creates linear regression lines for each frame on the true and false cords, the midline and the aryepiglottis.
    :param commissure:
    :param true_points_r:
    :param true_points_l:
    :return: (midlines, true_lines_l, true_lines_r, false_lines_l, false_lines_r, aryepiglottis_lines_l, aryepiglottis_lines_r)
        midlines: the midlines of the cords
        true_lines_l: lines of the left true cord
        true_lines_r: lines of the right true cord
        false_lines_l: lines of the left false cord
        false_lines_r: lines of the left false cord
        aryepiglottis_lines_l: the lines of the left aryepiglottis.
        aryepiglottis_lines_r: the lines of the right aryepiglottis.
    """
    frames = commissure.shape[0]
    comm_3d = commissure.reshape((1, frames, commissure.shape[1]))
    midline_points = np.concatenate((comm_3d, midline_points), axis=0)
    true_points_r = np.concatenate((comm_3d, true_points_r), axis=0)
    true_points_l = np.concatenate((comm_3d, true_points_l), axis=0)
    # true_angles = c
    # true_angles_l = np.empty(shape=comm.shape[0], dtype=np.float_)
    # true_angles_r = np.empty(shape=comm.shape[0], dtype=np.float_)
    # true_angles[:] = np.nan
    # true_angles_l[:] = np.nan
    # true_angles_r[:] = np.nan
    true_lines_l = np.empty(shape=(midline_points.shape[0], 4), dtype=np.float_)
    true_lines_r = [None] * frames
    false_lines_l = [None] * frames
    false_lines_r = [None] * frames
    aryepiglottis_lines_l = [None] * frames
    aryepiglottis_lines_r = [None] * frames
    midlines = [None] * commissure.shape[0]
    comms_there = np.logical_not(np.isnan(commissure).any(axis=1))
    # a list of booleans for each commisure point that is true if either coordinate in the point is nan
    for i in range(commissure.shape[0]):
        # filter out nan values
        midline_points_f = midline_points[
            np.logical_not(np.isnan(midline_points[:, i]).any(axis=2)), i
        ]
        true_points_l_f = true_points_l[
            np.logical_not(np.isnan(true_points_l[:, i]).any(axis=1)), i
        ]
        true_points_r_f = true_points_r[
            np.logical_not(np.isnan(true_points_r[:, i]).any(axis=1)), i
        ]
        false_points_l_f = false_points_l[
            np.logical_not(np.isnan(false_points_l[:, i]).any(axis=1)), i
        ]
        false_points_r_f = false_points_r[
            np.logical_not(np.isnan(false_points_r[:, i]).any(axis=1)), i
        ]
        # checks if there are less than 3 points in left_points[:,i] and left_points[:, i] with no nan coordinate
        if midline_points.shape[0] > 3:
            midlines[i] = regression_line(midline_points_f)
        if true_points_l_f.shape[0] >= 3 and true_points_r_f.shape[0] >= 3:
            true_lines_l[i] = cord_line(true_points_l_f, comms_there[i])
            true_lines_r[i] = cord_line(true_points_r_f, comms_there[i])
            if not true_lines_l[i] is None and not true_lines_r[i] is None:
                true_lines_l[i] = _set_ends(true_lines_l[i], true_points_l_f)
                true_lines_r[i] = _set_ends(true_lines_r[i], true_points_r_f)
                if true_lines_r[i].slope < 0 < true_lines_l[i].slope:
                    true_lines_r[i] = None
                    true_lines_l[i] = None
        if false_points_l_f.shape[0] >= 3 and false_points_r_f >= 3:
            false_lines_l[i] = regression_line(false_points_l_f)
            false_lines_r[i] = regression_line(false_points_r_f)
            if false_lines_l[i] is not None and not false_lines_r[i] is None:
                false_lines_l[i] = _set_ends(false_lines_l[i], false_points_l_f)
                false_lines_r[i] = _set_ends(false_lines_r[i], false_points_r_f)
                if false_lines_l[i].slope < 0 < false_lines_l[i].slope:
                    false_lines_l[i] = None
                    false_lines_r[i] = None
            # true_angles[i] = angle_between_lines(true_lines_l[i].slope, true_lines_r[i].slope)
            # if not midlines[i] is None:
            #     # calculate left and right angles
            #     true_angles_l[i] = angle_between_lines(true_lines_l[i].slope, midlines[i].slope)
            #     true_angles_r = true_angles[i] - true_angles_l[i]
            #     true_angles_r[i] = -(true_angles[i] - true_angles_l[i])
    return (
        midlines,
        true_lines_l,
        true_lines_r,
        false_lines_l,
        false_lines_r,
        aryepiglottis_lines_l,
        aryepiglottis_lines_r,
    )


@njit()
def dist(point0: np.ndarray, point1: np.ndarray):
    """
    calculates euclidian distance between 2 coordinates in a 2d space

    exists because scipy.spatial.distance.euclidian is not arraywise
    :param point0:
    :param point1:
    :return:
    """
    return np.sqrt(np.abs(point1[0] - point0[0]) ** 2 + np.abs((point1[1] - point0[1]) ** 2))


@njit()
def calc_angles_lengths(
    midlines,
    true_lines_l,
    true_lines_r,
    false_lines_l,
    false_lines_r,
    aryepiglottis_lines_l,
    aryepiglottis_lines_r,
):
    true_angles = angle_between_lines(true_lines_l["slope"], true_lines_r["slope"])
    true_angles_l = angle_between_lines(true_lines_l["slope"], midlines["slope"])
    true_angles_r = true_angles - true_angles_l
    false_angles = angle_between_lines(false_lines_l["slope"], false_lines_r["slope"])
    false_angles_l = angle_between_lines(false_lines_l["slope"], midlines["slope"])
    false_angles_r = false_angles - false_angles_l
    true_lengths_l = dist(true_lines_l["end0"], true_lines_l["end1"])
    true_lengths_r = dist(true_lines_r["end0"], true_lines_r["end1"])
    length_false_l = dist(false_lines_l["end0"], false_lines_l["end1"])
    length_false_r = dist(false_lines_r["end0"], false_lines_r["end1"])

    return (
        true_angles,
        true_angles_l,
        true_angles_r,
        false_angles,
        false_angles_l,
        false_angles_r,
        true_lengths_l,
        true_lengths_r,
        length_false_l,
        length_false_r,
    )


@njit()
def calc_cord_widths(left_true_points,
                     right_true_points,
                     left_false_points,
                     right_false_points):
    width_l = dist(left_true_points, left_false_points)
    width_r = dist(right_true_points, right_false_points)


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
            midlines,
            true_lines_l,
            true_lines_r,
            false_lines_l,
            false_lines_r,
            aryepiglottis_lines_l,
            aryepiglottis_lines_r,
        ) = create_lines(
            midline_points,
            commissure,
            left_true_points,
            right_true_points,
            left_false_points,
            right_false_points,
            left_aeglottis_points,
            right_aeglottis_points,
        )

        calc_angles_lengths(midlines, true_lines_l,
            true_lines_r, false_lines_l,
            false_lines_r, aryepiglottis_lines_l, aryepiglottis_lines_r)
        # what is this doing?
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
    if pf.rvalue**2 < 0.9:
        pfc = outlier_del(pfx, pfy, comm, pf)
        if abs(pfc.rvalue) > abs(pf.rvalue):
            pf = pfc
    if pf.rvalue**2 < 0.8:
        return
    return slope_line(slope=pf.slope, intercept=pf.intercept)


def regression_line(points: np.ndarray, min_r2=0.9) -> [Line]:
    linreg = stats.linregress(points)
    if linreg.rvalue**2 > min_r2:
        return slope_line(linreg.slope, linreg.intercept)
    return None


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
