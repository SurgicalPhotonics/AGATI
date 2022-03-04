import csv
import os
import cv2
import dlc_generic_analysis as dga
import numpy as np
import pandas as pd
from scipy import stats
from draw import draw
from matplotlib import pyplot as plt
from tqdm import tqdm
from numba import njit

nan_l = np.zeros(6)
nan_l[:] = np.nan


def nan_line():
    return nan_l.copy()


PET_NAME = ["PET"]
ANTERIOR_COMMISSURE_NAME = ["AC"]
LEFT_TRUE_CORD_NAMES = ["LC" + str(i) for i in range(1, 7)]
RIGHT_TRUE_CORD_NAMES = ["RC" + str(i) for i in range(1, 7)]
LEFT_FALSE_CORD_NAMES = ["LFC" + str(i) for i in range(1, 7)]
RIGHT_FALSE_CORD_NAMES = ["RFC" + str(i) for i in range(1, 7)]
MIDLINE_NAMES = ["ML" + str(i) for i in range(1, 4)]
RIGHT_ARYEPIGLOTTIS_NAMES = ["RAE" + str(i) for i in range(1, 6)]
LEFT_ARYEPIGLOTTIS_NAMES = ["LAE" + str(i) for i in range(1, 6)]


@njit()
def _slope_line(slope: np.float_, intercept: np.float_):
    return np.array([slope, intercept, 0, intercept, 1, int(intercept + slope)], dtype=np.float_)


@njit()
def _points_line(end0, end1):
    if not end1[0] == end0[0]:
        slope = (end1[1] - end0[1]) / (end1[0] - end0[0])
    else:
        slope = 9e9
    return np.array(
        [slope, end0[1] - slope * end0[0], end0[0], end0[1], end1[0], end1[1]], dtype=np.float_
    )


def _set_ends(line: np.ndarray, points: "np.ndarray") -> "np.ndarray":
    """
    sets the ends of a line to the outermost points
    :param line:
    :param points:
    :return:
    """
    c = points[np.logical_not(np.isnan(points).any(axis=1))]
    y = c[points.shape[0] - 1, 1]
    if line[0] != 0:
        line[4] = int((y - line[1]) / line[0])
        line[5] = int(y)
    else:
        line[4] = 1
        line[5] = int(y)
    y = c[0][1]
    if line[0] != 0:
        line[2] = int((y - line[1]) / line[0])
        line[3] = int(y)
    else:
        line[2] = 1
        line[3] = int(y)
    return line


def analyze(model_config: str, video_paths: [str]):
    """
    Analyze a list of videos
    :param model_config: the path to the directory containing the config.yaml file
    :param video_paths: the videos to analyze
    :return:
    """
    h5s, dlc_scorer = dga.dlc_analyze(model_config, video_paths)
    h5s = dga.filter.threshold_confidence(h5s, 0.85)
    for i in range(len(h5s)):
        analysis = Analysis(h5s[i], dlc_scorer, video_paths[i])
        analysis.write_csv()
        analysis.draw()
        analysis.plot()


@njit()
def _angle_between_lines(slope0: np.float_, slope1: np.float_):
    return np.degrees(np.arctan(slope0 - slope1) / (1 + slope0 * slope1))


def _create_lines(
    midline_points: np.ndarray,
    commissure: np.ndarray,
    true_points_l: np.ndarray,
    true_points_r: np.ndarray,
    false_points_l: np.ndarray,
    false_points_r: np.ndarray,
    aryepiglottis_points_l: np.ndarray,
    aryepiglottis_points_r: np.ndarray,
) -> ("np.ndarray" * 7):
    """
    Creates linear regression lines for each frame on the true and false cords, the midline and the aryepiglottis.
    :param midline_points:
    :param commissure:
    :param true_points_l:
    :param true_points_r:
    :param false_points_l:
    :param false_points_r:
    :param aryepiglottis_points_l:
    :param aryepiglottis_points_r:
    :return: (midlines, true_lines_l, true_lines_r, false_lines_l, false_lines_r, aeglottis_lines_l, aeglottis_lines_r)
        midlines: the midlines of the cords
        true_lines_l: lines of the left true cord
        true_lines_r: lines of the right true cord
        false_lines_l: lines of the left false cord
        false_lines_r: lines of the left false cord
        aeglottis_lines_l: the lines of the left aryepiglottis.
        aeglottis_lines_r: the lines of the right aryepiglottis.
    """
    frames = commissure.shape[0]
    line_shape = (frames, 6)
    comm_3d = commissure.reshape((1, frames, commissure.shape[1]))
    midline_points = np.concatenate((comm_3d, midline_points), axis=0)
    true_points_r = np.concatenate((comm_3d, true_points_r), axis=0)
    true_points_l = np.concatenate((comm_3d, true_points_l), axis=0)
    aeglottis_lines_l = np.empty(shape=line_shape, dtype=np.float_)
    aeglottis_lines_r = aeglottis_lines_l.copy()
    comms_there = np.logical_not(np.isnan(commissure).any(axis=1))
    midlines = aeglottis_lines_l.copy()
    true_lines_l = aeglottis_lines_l.copy()
    true_lines_r = aeglottis_lines_l.copy()
    false_lines_l = aeglottis_lines_l.copy()
    false_lines_r = aeglottis_lines_l.copy()
    "creating lines"
    for i in tqdm(range(frames)):
        (
            midlines[i],
            true_lines_l[i],
            true_lines_r[i],
            false_lines_l[i],
            false_lines_r[i],
            aeglottis_lines_l[i],
            aeglottis_lines_r[i],
        ) = create_lines_func(
            midline_points[:, i],
            comms_there[i],
            true_points_l[:, i],
            true_points_r[:, i],
            false_points_l[:, i],
            false_points_r[:, i],
            aryepiglottis_points_l[:, i],
            aryepiglottis_points_r[:, i],
        )
    return (
        midlines,
        true_lines_l,
        true_lines_r,
        false_lines_l,
        false_lines_r,
        aeglottis_lines_l,
        aeglottis_lines_r,
    )


def filter_nan_points(points: np.ndarray):
    return points[np.logical_not(np.isnan(points).any(axis=1))]


def create_lines_func(
    midline_points: "np.ndarray",
    comm_there: "np.ndarray",
    true_points_l: "np.ndarray",
    true_points_r: "np.ndarray",
    false_points_l: "np.ndarray",
    false_points_r: "np.ndarray",
    aeglottis_points_l: "np.ndarray",
    aeglottis_points_r: "np.ndarray",
) -> ("np.ndarray" * 7):
    """
    Creates Linear regression lines for the midline, left and right true and false cords from the depelabcut points
    :param midline_points:
    :param comm_there:
    :param true_points_l:
    :param true_points_r:
    :param false_points_l:
    :param false_points_r:
    :param aeglottis_points_l:
    :param aeglottis_points_r:
    :return:
    """
    # filters out nan values from point arrays
    midline_points_f = filter_nan_points(midline_points)
    true_points_l_f = filter_nan_points(true_points_l)
    true_points_r_f = filter_nan_points(true_points_r)
    false_points_l_f = filter_nan_points(false_points_l)
    false_points_r_f = filter_nan_points(false_points_r)
    aeglottis_points_l_f = filter_nan_points(aeglottis_points_l)
    aeglottis_points_r_f = filter_nan_points(aeglottis_points_r)
    # checks if there are less than 3 points in left_points[:,i] and left_points[:, i] with no nan coordinate
    if midline_points_f.shape[0] >= 3:
        midline = _regression_line(midline_points_f)
    else:
        midline = nan_line()
    if true_points_l_f.shape[0] >= 3 and true_points_r_f.shape[0] >= 3:
        true_line_l = _cord_line(true_points_l_f, comm_there)
        true_line_r = _cord_line(true_points_r_f, comm_there)
        if not np.isnan(true_line_l[0]) and not np.isnan(true_line_r[0]):
            if true_line_r[0] < 0 < true_line_l[0]:
                true_line_r = nan_line()
                true_line_l = nan_line()
    else:
        true_line_l = nan_line()
        true_line_r = nan_line()
    if false_points_l_f.shape[0] >= 3 and false_points_r_f.shape[0] >= 3:
        false_line_l = _regression_line(false_points_l_f)
        false_line_r = _regression_line(false_points_r_f)
        if not np.isnan(false_line_l[0]) and not np.isnan(false_line_r[0]):
            if false_line_r[0] < 0 < false_line_l[0]:
                false_line_l = nan_line()
                false_line_r = nan_line()
    else:
        false_line_l = nan_line()
        false_line_r = nan_line()
    if aeglottis_points_l_f.shape[0] >= 3 and aeglottis_points_r_f.shape[0] >= 3:
        aeglottis_line_l = _regression_line(aeglottis_points_l_f)
        aeglottis_line_r = _regression_line(aeglottis_points_r_f)
    else:
        aeglottis_line_l = nan_line()
        aeglottis_line_r = nan_line()

    return (
        midline,
        true_line_l,
        true_line_r,
        false_line_l,
        false_line_r,
        aeglottis_line_l,
        aeglottis_line_r,
    )


@njit()
def dist(point0: np.ndarray, point1: np.ndarray):
    """
    calculates euclidian distance between 2 coordinates in a 2d space
    exists because scipy.spatial.distance.euclidian is not elementwise
    :param point0: the first x,y coordinate
    :param point1: the second x,y coordinate
    :return:
    """
    return np.sqrt(
        np.power(np.abs(point1[:, 0] - point0[:, 0]), 2)
        + np.power(np.abs(point1[:, 1] - point0[:, 1]), 2)
    )


# @njit()
def _calc_angles_lengths(
    midlines,
    true_lines_l,
    true_lines_r,
    false_lines_l,
    false_lines_r,
    aryepiglottis_lines_l,
    aryepiglottis_lines_r,
    true_points_l,
    true_points_r,
    false_points_l,
    false_points_r,
) -> ("np.ndarray" * 10):
    """

    :param midlines:
    :param true_lines_l:
    :param true_lines_r:
    :param false_lines_l:
    :param false_lines_r:
    :param aryepiglottis_lines_l:
    :param aryepiglottis_lines_r:
    :return:
        true_angles: the anterior glottic angle
        true_angles_l: the angle between the left true cord and the midline
        true_angles_r: the angle between the right true cord and the midline
        false_angles: the angle between the false cords
        false_angles_l: the angle between the left false cord and the midline
        false_angles_r: the angle between the right false cord and the midline
        aeg_tvc_l: the angle between the left aeryepiglottic fold and the left true vocal fold
        aeg_tvc_r: the angle between the right aeryepiglottic fold and the right true vocal fold
        true_lengths_l: the distance between anterior commisure and the end of the left vocal fold
        true_lengths_r: the distance between anterior commisure and the end of the right vocal fold
        false_lengths_l: the distance between first and last point on the left false cord
        false_lengths_r: the distance between first and last point on the left right cord
    """
    true_angles = _angle_between_lines(true_lines_l[:, 0], true_lines_r[:, 0])
    true_angles_l = _angle_between_lines(true_lines_l[:, 0], midlines[:, 0])
    true_angles_r = true_angles - true_angles_l
    false_angles = _angle_between_lines(false_lines_l[:, 0], false_lines_r[:, 0])
    false_angles_l = _angle_between_lines(false_lines_l[:, 0], midlines[:, 0])
    false_angles_r = false_angles - false_angles_l
    true_lengths_l = dist(true_points_l[0], true_points_l[-1])
    true_lengths_r = dist(true_points_r[0], true_points_r[-1])
    false_lengths_l = dist(false_points_l[0], false_points_l[-1])
    false_lengths_r = dist(false_points_r[0], false_points_r[-1])
    aeg_tvc_l = _angle_between_lines(aryepiglottis_lines_l[:, 0], true_lines_l[:, 0])
    aeg_tvc_r = _angle_between_lines(aryepiglottis_lines_r[:, 0], true_lines_r[:, 0])
    return (
        true_angles,
        true_angles_l,
        true_angles_r,
        false_angles,
        false_angles_l,
        false_angles_r,
        aeg_tvc_l,
        aeg_tvc_r,
        true_lengths_l,
        true_lengths_r,
        false_lengths_l,
        false_lengths_r,
    )


def _calc_cord_widths(
    true_points_l: "np.array",
    true_points_r: "np.array",
    false_points_l: "np.array",
    false_points_r: "np.array",
) -> ("np.ndarray" * 2):
    average_widths_l = np.zeros(shape=true_points_l.shape[1])
    average_widths_r = average_widths_l.copy()
    for i in range(true_points_l.shape[1]):
        if (
            true_points_l[np.logical_not(np.isnan(true_points_l[:, i]).any(axis=1)), i].shape[0]
            >= 3
            and false_points_l[np.logical_not(np.isnan(false_points_l[:, i]).any(axis=1)), i].shape[
                0
            ]
            >= 3
        ):
            width_l = dist(true_points_l[:, i], false_points_l[:, i])
            average_widths_l[i] = np.nanmean(width_l, axis=0)
        else:
            average_widths_l[i] = np.nan
        if (
            true_points_r[np.logical_not(np.isnan(true_points_r[:, i]).any(axis=1)), i].shape[0]
            >= 3
            and false_points_r[np.logical_not(np.isnan(false_points_r[:, i]).any(axis=1)), i].shape[
                0
            ]
            >= 3
        ):
            width_r = dist(true_points_r[:, i], false_points_r[:, i])
            average_widths_r[i] = np.nanmean(width_r, axis=0)
        else:
            average_widths_r[i] = np.nan
    return average_widths_l, average_widths_r


class Analysis(dga.Analysis):
    def write_csv(self):
        pass

    def __init__(
        self, h5_path: str, dlc_scorer: str, video_path: str, export="metrics", filetype=".h5"
    ):
        h5_path = os.path.abspath(h5_path)
        if not os.path.isfile(h5_path):
            raise FileNotFoundError(h5_path)
        dga.Analysis.__init__(self, h5_path, dlc_scorer)
        self.video_path = video_path
        self.out_file = None
        midline_points = np.squeeze(dga.utils.point_array(self.df, MIDLINE_NAMES))
        true_points_r = np.squeeze(dga.utils.point_array(self.df, RIGHT_TRUE_CORD_NAMES))
        true_points_l = np.squeeze(dga.utils.point_array(self.df, LEFT_TRUE_CORD_NAMES))
        false_points_r = np.squeeze(dga.utils.point_array(self.df, RIGHT_FALSE_CORD_NAMES))
        false_points_l = np.squeeze(dga.utils.point_array(self.df, LEFT_FALSE_CORD_NAMES))
        aeglottis_points_r = np.squeeze(dga.utils.point_array(self.df, RIGHT_ARYEPIGLOTTIS_NAMES))
        aeglottis_points_l = np.squeeze(dga.utils.point_array(self.df, LEFT_ARYEPIGLOTTIS_NAMES))
        commissure = np.squeeze(dga.utils.point_array(self.df, ANTERIOR_COMMISSURE_NAME))
        (
            midlines,
            true_lines_l,
            true_lines_r,
            false_lines_l,
            false_lines_r,
            aryepiglottis_lines_l,
            aryepiglottis_lines_r,
        ) = _create_lines(
            midline_points,
            commissure,
            true_points_l,
            true_points_r,
            false_points_l,
            false_points_r,
            aeglottis_points_l,
            aeglottis_points_r,
        )
        (
            true_angles,
            true_angles_l,
            true_angles_r,
            false_angles,
            false_angles_l,
            false_angles_r,
            aeg_true_l,
            aeg_true_r,
            true_lengths_l,
            true_lengths_r,
            false_lengths_l,
            false_lengths_r,
        ) = _calc_angles_lengths(
            midlines,
            true_lines_l,
            true_lines_r,
            false_lines_l,
            false_lines_r,
            aryepiglottis_lines_l,
            aryepiglottis_lines_r,
            true_points_l,
            true_points_r,
            false_points_l,
            false_points_r,
        )
        percentile_97 = np.nanpercentile(true_angles, 97)
        true_angles_filtered = true_angles[np.logical_not(np.isnan(true_angles))]
        display_angles = np.where(true_angles_filtered < percentile_97, true_angles_filtered, 0)
        self.display_angles = display_angles
        vid = cv2.VideoCapture(self.video_path)
        frame_rate = vid.get(cv2.CAP_PROP_FPS)
        # compute cord velocities in degrees / second
        self.velocities = np.zeros(shape=true_angles.shape[0])
        self.velocities[0] = np.nan
        print("computing velocities")
        for i in tqdm(range(1, true_angles.shape[0] - 1)):
            if not np.isnan(true_angles[i]) and np.isnan(true_angles[i + 1]):
                self.velocities[i] = (true_angles[i + 1] - true_angles[i]) * frame_rate
            else:
                self.velocities[i] = np.nan
        # compute accelerations in degrees / second^2
        self.accelerations = np.zeros(shape=true_angles.shape[0])
        self.accelerations[0] = np.nan
        print("computing accelerations")
        for i in tqdm(range(1, self.velocities.shape[0])):
            if not np.isnan(self.velocities[i]) and not np.isnan(self.velocities[i - 1]):
                self.accelerations[i] = self.velocities[i] - self.velocities[i - 1]
        cord_widths_l, cord_widths_r = _calc_cord_widths(
            true_points_l, true_points_r, false_points_l, false_points_r
        )
        self.true_angles = true_angles
        self.true_angles_l = true_angles_l
        self.true_angles_r = true_angles_r
        self.true_lengths_l = true_lengths_l
        self.true_lengths_r = true_lengths_r

        self.false_angles = false_angles
        self.false_angles_l = false_angles_l
        self.false_angles_r = false_angles_r

        self.midlines = midlines

        self.aeg_true_l = aeg_true_l
        self.aeg_true_r = aeg_true_r

        self.true_lines_l = true_lines_l
        self.true_lines_r = true_lines_r
        self.aeg_true_l = aeg_true_l
        self.aeg_true_r = aeg_true_r
        self.false_lines_l = false_lines_l
        self.false_lines_r = false_lines_r
        self.aryepiglottis_lines_l = aryepiglottis_lines_l
        self.aryepiglottis_lines_r = aryepiglottis_lines_r
        self.cord_widths_l = cord_widths_l
        self.cord_widths_r = cord_widths_r
        if export.lower() == "metrics" or export.lower() == "all":
            true = pd.DataFrame(
                {
                    "angles": self.true_angles,
                    "angles_l": self.true_angles_l,
                    "angles_r": self.true_angles_r,
                }
            )
            false = pd.DataFrame(
                {
                    "angles": self.false_angles,
                    "angles_l": self.false_angles_l,
                    "angles_r": self.false_angles_r,
                }
            )
            aeg_true = pd.DataFrame(
                {
                    "angle_l": self.aeg_true_l,
                    "angle_r": self.aeg_true_r,
                }
            )
            cord_widths = pd.DataFrame(
                {
                    "l": self.cord_widths_l,
                    "r": self.cord_widths_r,
                }
            )
            key = os.path.split(os.path.splitext(video_path)[0])[1] + "_analyzed"
            if export is None:
                pass
            elif export == "metrics":
                df = pd.concat([true, false, aeg_true, cord_widths], keys=["true", "false", "aeg_true", "cord_widths"], axis=1)
                df = pd.concat([df], keys=[key], names=["File"], axis=1)
            elif export == "all":
                midlines = _df_line(self.midlines)
                true_lines_l = _df_line(self.true_lines_l)
                true_lines_r = _df_line(self.true_lines_r)
                false_lines_l = _df_line(self.false_lines_l)
                false_lines_r = _df_line(self.false_lines_r)
                aryepiglottis_lines_l = _df_line(self.aryepiglottis_lines_l)
                aryepiglottis_lines_r = _df_line(self.aryepiglottis_lines_r)
                lines = pd.concat(
                    [
                        midlines,
                        true_lines_l,
                        true_lines_r,
                        false_lines_l,
                        false_lines_r,
                        aryepiglottis_lines_l,
                        aryepiglottis_lines_r,
                    ],
                    keys=[
                        "midlines",
                        "true_lines_l",
                        "true_lines_r",
                        "false_lines_l",
                        "false_lines_r",
                        "aryepiglottis_lines_l",
                        "aryepiglottis_lines_r",
                    ],
                )
                df = pd.concat(
                    [true, false, aeg_true, cord_widths,  lines],
                    keys=["true", "false", "aeg_true", "cord_widths", "lines"],
                    axis=1,
                )
                df = pd.concat([df], keys=[key], names=["File"], axis=1)
            else:
                raise AttributeError
            data_path = os.path.splitext(video_path)[0] + "_analyzed"
            if filetype == ".h5" or filetype == "h5":
                data_path = data_path + ".h5"
                df.to_hdf(data_path, key=key)
            print(f"Saving analysis data to {data_path}.")

    def draw(self, outfile: str = None):
        self.out_file = draw(
            self.video_path,
            self.midlines,
            self.true_lines_l,
            self.true_lines_r,
            self.false_lines_l,
            self.false_lines_r,
            self.aryepiglottis_lines_l,
            self.aryepiglottis_lines_r,
            self.true_angles,
            outfile,
        )

    def write_file(self, file_path: str = None):

        if file_path is None:
            if self.out_file is not None:
                file_path = os.path.splitext(self.out_file)[0] + ".csv"
            else:
                file_path = os.path.splitext(self.video_path)[0] + "_analyzed.csv"

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


def _df_line(array: np.ndarray):
    return _df_line_nparray(array[:, 0], array[:, 1], array[:, 2:4], array[:, 4:6])


def _df_line_nparray(
    slope: "np.ndarray", intercept: "np.ndarray", end0: "np.ndarray", end1: "np.ndarray"
) -> pd.DataFrame:
    """
    creates a dataframe line from numpy arrays
    :param slope: the line slope values
    :param intercept: the line intercept values
    :param end0: The point coordinates for the 0th end of the line
    :param end1: The point coordinates for the first end of the line
    :return:
    """
    mx_b = pd.DataFrame({"slope": slope, "intercept": intercept})
    end0 = pd.DataFrame({"x": end0[0], "y": end0[1]})
    end1 = pd.DataFrame({"x": end1[0], "y": end1[1]})
    ends = pd.concat([end0, end1], keys=["end0", "end1"], axis=1)
    return pd.concat([mx_b, ends], axis=1)


def _cord_line(points, comm) -> "np.ndarray":
    """
    Given a list corresponding to points plotted on a vocal cord. Calculates
    a regression line from those points which is used to represent the cord.
    :param points: the points to use to create the line
    :param comm: the commissure point
    :return: if a line representing the edge of a vocal cord.
    """
    pfx = points[:, 0]
    pfy = points[:, 1]
    linreg = stats.linregress(pfx, pfy)
    if comm and len(pfx) > 3:
        pfc = stats.linregress(pfx[1:], pfy[1:])
        if abs(pfc.rvalue) > abs(linreg.rvalue):
            linreg = pfc
    if linreg.rvalue**2 < 0.9:
        pfc = _outlier_del(pfx, pfy, comm, linreg)
        if abs(pfc.rvalue) > abs(linreg.rvalue):
            linreg = pfc
    if linreg.rvalue**2 < 0.8:
        return nan_line()
    if linreg is not None:
        line = _slope_line(slope=linreg.slope, intercept=linreg.intercept)
        line = _set_ends(line, points)
        return line


def _regression_line(points: np.ndarray, min_r2=0.9) -> "np.ndarray":
    linreg = stats.linregress(points)
    if linreg.rvalue**2 > min_r2:
        line = _slope_line(linreg.slope, linreg.intercept)
        line = _set_ends(line, points)
        return line
    return nan_line()


def _outlier_del(points_x: np.ndarray, point_y: np.ndarray, comm: bool, linreg):
    """
    Deletes outliers from sufficiently large cord lists.
    :param points_x: x point values
    :param point_y: y point values
    :param comm:
    :param linreg:
    :return:
    """
    if comm:
        points_x = points_x[1:]
        point_y = point_y[1:]
    if len(points_x) > 3:
        for i in range(len(points_x) - 1):
            newx = points_x[:-1]
            newy = point_y[:-1]
            newline = stats.linregress(newx, newy)
            if len(newx) > 3:
                newline = _outlier_del(newx, newy, False, newline)
            if newline.rvalue > linreg.rvalue:
                linreg = newline
    return linreg
