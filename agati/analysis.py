import csv
import os
import typing
import cv2
import dlc_generic_analysis as dga
import numpy as np
from scipy import stats
from draw import draw
from dlc_generic_analysis.geometries import Line
from numba import njit
from numba.typed import List
import numpy.typing as npt
from matplotlib import pyplot as plt

COMMISSURE_NAME = ["AC"]
LEFT_NAMES = ["LC1", "LC2", "LC3", "LC4", "LC5", "LVP"]
RIGHT_NAMES = ["RC1", "RC2", "RC3", "RC4", "RC5", "RVP"]
NDArrayF64 = npt.NDArray[np.float64]


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
    for i in range(len(h5s)):
        analysis = Analysis(h5s[i], dlc_scorer, video_paths[i])
        analysis.write_csv()
        analysis.draw()
        analysis.plot()


@njit()
def alt_angle(
    left_cord, right_cord, comm_there
) -> typing.Tuple[np.float64, np.float64, np.ndarray, np.ndarray]:
    """
    Alternative anterior glottic angle of opening calculation.
    :param left_cord: the points the left vocal cord
    :param right_cord: the points onn the right vocal cord
    :param comm_there: # if there is a comm in the left_cord and right_cord lists
    :return: (angle, lret, left, right)
        angle: the angle between the 2 cords in degrees
        lret: # ask Nat
        left: the left cord line
        right: the right cord line
    """
    left_line = calc_reg_line(left_cord, comm_there)
    right_line = calc_reg_line(right_cord, comm_there)
    left = left_line
    right = right_line
    if left_line is None or right_line is None:
        return np.nan, np.nan, left, right
    left_line = _set_ends(left_line, left_cord)
    right_line = _set_ends(right_line, right_cord)
    tan = abs((left_line[0] - right_line[0]) / (1 + left_line[0] * right_line[0]))
    # Angles of cords from vertical midline
    ladj = left_line.end2[0] - left_line.end1[0]
    lop = abs(left_line.end2[1] - left_line.end1[1])
    if ladj == 0:
        ladj = 0.00001
    angle_l = np.degrees(np.atan(lop / ladj))
    if left_line.slope < 0:
        lret = 90 - angle_l
    else:
        lret = -angle_l - 90
    return np.atan(tan), lret, left, right


def _calc_lines_angles(
    comm: np.ndarray, right_points: np.ndarray, left_points: np.ndarray
) -> typing.Tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, typing.List[Line], typing.List[Line]
]:
    """

    :param comm:
    :param right_points:
    :param left_points:
    :return: (angles_filtered, angels, angles_l, angle_r, line_l, line_r)
        angles_filtered np.ndarray: anterior glottic angle with nan vales removed
        angles np.ndarray:: The anterior glottic angle for each frame.
        angles_l np.ndarray: the angle of the line_l cord.
        angle_r np.ndarray: the angle of the line_r cord.
        line_l: the line of the left cord edge
        line_r: the line of the right cord edge.
    """
    right_points = right_points[np.logical_not(np.isnan(right_points))]
    left_points = left_points[np.logical_not(np.isnan(left_points))]
    return __calc_angle_helper(comm, right_points, left_points)


@njit()
def __calc_angle_helper(
    comm: np.ndarray, right_points: np.ndarray, left_points: np.ndarray,
):
    angles = np.zeros(shape=comm.shape[0], dtype=np.float_)
    angles_l = angles
    angles_r = angles
    line_l = np.zeros(shape=(comm.shape[0], 2), dtype=np.float_)
    line_r = line_l
    for i in range(len(comm)):
        cords_there = True
        comm_there = np.logical_not(np.isnan(comm))
        if right_points.shape[0] < 3:
            cords_there = False
        if left_points.shape[0] < 3:
            cords_there = False
        if cords_there:
            angles[i], angles_l[i], line_l[i], line_r[i] = alt_angle(
                left_points[i], right_points[i], comm_there
            )
            if not np.isnan(angles_l[i]):
                angles_r[i] = -(angles * 180 / np.pi - angles_l)
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
    angles_filered = angles[np.logical_not(np.isnan(angles))] * 180 / np.pi
    angles = angles * 180 / np.pi
    return angles_filered, angles, angles_l, angles_r, line_l, line_r


class Analysis(dga.Analysis):
    def __init__(self, h5_path: str, dlc_scorer: str, video_path: str):
        h5_path = os.path.abspath(h5_path)
        if not os.path.isfile(h5_path):
            raise FileNotFoundError(h5_path)
        dga.Analysis.__init__(self, h5_path, dlc_scorer)
        self.video_path = video_path
        self.out_file = None
        right_points = dga.utils.point_array(self.df, RIGHT_NAMES)
        left_points = dga.utils.point_array(self.df, LEFT_NAMES)
        commissure = dga.utils.point_array(self.df, COMMISSURE_NAME)
        self.angles_filtered, self.angles, lang, rang, self.left, self.right = _calc_lines_angles(
            commissure, right_points, left_points
        )
        # WTF is this doing
        display_angles = List()
        count = 0
        percentile_97 = np.percentile(self.angles_filtered, 97)
        print(f"97th percentile = {percentile_97}")
        for i in range(self.angles):
            if np.isnan(self.angles[i]) and np.isnan(lang) and np.isnan(rang):
                display_angles.append(np.nan)
            elif np.isnan(self.angles[i]):
                display_angles.append(np.nan)
            elif self.angles_filtered[i] > percentile_97:
                display_angles.append(0)
                count += 1
            else:
                display_angles.append(self.angles_filtered[count])
                count += 1
        self.angles_transformed = self.angles
        self.display_angles = np.array(display_angles)
        vid = cv2.VideoCapture(self.video_path)
        frames = vid.get(cv2.CAP_PROP_FPS)
        vels = np.ndarray(self.angles_transformed.shape[0])
        dif = 1
        for i in range(1, len(self.display_angles)):
            if (
                np.isnan(self.angles_transformed[i]) or self.angles_transformed[i - dif] is None
            ):  # WTF is this checking for
                vels.append(np.nan)
                dif = 1
            elif not np.isnan(self.angles_transformed[i - 1]):
                vels.append(
                    (self.angles_transformed[i] - self.angles_transformed[i] - dif) * frames / dif
                )
                dif = 1
            elif np.isnan(self.angles_transformed[i - dif]):
                i += 1
                vels.append(None)
            else:
                vels.append(None)
                i += 1
                dif += 1
        acels = [0]
        dif = 1
        for i in range(1, len(vels)):
            if vels[i] is not None and vels[i - dif] is not None:
                acels.append((vels[i] - vels[i - dif]) * frames / dif)
                dif = 1
            elif vels[i - dif] is None:
                i += 1
            else:
                i += 1
                dif += 1
        acels = np.ndarray(acels)
        self.velocities = vels
        self.accelerations = acels

    def draw(self, outfile: str = None):
        if outfile is None:
            file, ext = os.path.splitext(outfile)
            outfile = file + "_analyzed" + ext
        self.out_file = draw(
            self.video_path, (self.left, self.right), self.angles, outfile, vidtype=ext
        )

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

    def angle_of_opening(self, left_cord, right_cord, comm):
        """Calculates angle of opening between left and right cord."""
        left_line = calc_reg_line(left_cord, comm)
        right_line = calc_reg_line(right_cord, comm)
        self.left.append(left_line)
        self.right.append(right_line)
        if left_line is None or right_line is None:
            return np.nan
        _set_ends(left_line, left_cord)
        _set_ends(right_line, right_cord)
        if right_line.slope < 0 < left_line.slope:
            return 0
        tan = abs((left_line.slope - right_line.slope) / (1 + left_line.slope * right_line.slope))
        return np.atan(tan)


@njit()
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
    return np.array([pf.slope, pf.intercept])


@njit()
def calc_muscular_line(pt_list, comm):
    """Calculates angle of opening by drawing straight line from anterior
    commisure if availible and most distal point on cord."""
    if pt_list[0] is not None:
        far_ind = 0
        for i in range(len(pt_list)):
            if pt_list[i] is not None:
                far_ind = i
        return Line(pt_list[0], pt_list[far_ind])
    else:
        return calc_reg_line(pt_list, comm)
