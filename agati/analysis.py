import csv
import os
import sys
import dlc_generic_analysis as dga
import numpy as np
from scipy import stats
COMMISSURE_NAME = ["AC"]
LEFT_NAMES = ["LC1","LC2",
    "LC3",
    "LC4",
    "LC5",
    "LVP"]
RIGHT_NAMES = [    "RC1",
    "RC2",
    "RC3",
    "RC4",
    "RC5",
    "RVP"]
def analyze(video_paths: [str], model_dir: str):
    h5s, dlc_scorer = dga.dlc_analyze(model_dir, video_paths)
    analysis = Analysis(h5s, dlc_scorer, video_paths)


class Analysis(dga.analysis):
    def __init__(self, h5_path: str, dlc_scorer: str, video_path: str):
        self.video_path = video_path
        dir_path = os.path.split(video_path)[0]
        h5_path = os.path.abspath(h5_path)
        if not os.path.isfile(h5_path):
            raise FileNotFoundError(h5_path)
        dga.Analysis.__init__(self, h5_path, dlc_scorer)
        right_points = dga.utils.point_array(self.df, RIGHT_NAMES)
        left_points = dga.utils.point_array(self.df, LEFT_NAMES)
        commissure = dga.utils.point_array(self.df, COMMISSURE_NAME)
        self.angles = np.array(shape=right_points.shape[0])
        self.lang = self.angles
        self.rang = self.lang
        for i in range(left_points.shape[0]):
            for item in left_points[i]:
                if item is not None:
                    num_pts += 1
            if num_pts < 3 and left_points[i, 0] is None:
                cords_there = False
            num_pts = 0
            for item in right_points[i]:
                if item is not None:
                    num_pts += 1
            if num_pts < 3 and right_points[i,0] is None:
                cords_there = False
            if cords_there:
                self.angles[i], self.lang[i] = self.alt_angle(left_points[i], right_points[i])
                if self.lang[i] is not None:
                    self.rang[i] = -(self.angles[i] * 180 / np.pi - self.lang[i])
                else:
                    self.rang[i] = np.nan
            else:
                self.angles[i] = np.nan
                self.lang[i] = np.nan
                self.rang[i] = np.nan


    def filter(self):

        for i in range(len(self.angles)):



    def alt_angle(self, left_cord, right_cord, comm):
        """
        Alternative anterior glottic angle of opening calculation.
        :param left_cord: the points the left vocal chord
        :param right_cord:
        :param comm:
        :return:
        """
        left_line = calc_reg_line(left_cord, comm)
        right_line = calc_reg_line(right_cord, comm)
        self.left.append(left_line)
        self.right.append(right_line)
        if left_line is None or right_line is None:
            return None, None
        left_line.set_ends(left_cord)
        right_line.set_ends(right_cord)
        if right_line.slope < 0 < left_line.slope:
            return 0, left_line.slope, right_line.slope
        tan = abs((left_line.slope - right_line.slope) / (1 + left_line.slope * right_line.slope))

        # Angles of cords from vertical midline
        ladj = left_line.end2[0] - left_line.end1[0]
        lop = abs(left_line.end2[1] - left_line.end1[1])
        if ladj == 0:
            ladj = 0.00001
        lang = np.degrees(np.atan(lop / ladj))
        if left_line.slope < 0:
            lret = 90 - lang
        else:
            lret = -lang - 90
        return np.atan(tan), lret

    def angle_of_opening(self, left_cord, right_cord, comm):
        """Calculates angle of opening between left and right cord."""
        left_line = calc_reg_line(left_cord, comm)
        right_line = calc_reg_line(right_cord, comm)
        self.left.append(left_line)
        self.right.append(right_line)
        if left_line is None or right_line is None:
            return None
        left_line.set_ends(left_cord)
        right_line.set_ends(right_cord)
        if right_line.slope < 0 < left_line.slope:
            return 0
        """cross = intersect(left_line, right_line)
        if cross is not None:
            crossy = cross[1]
        else:
            return 0
        if crossy > left_cord[0][1] + 20 or crossy > right_cord[0][1] + 20:
            return 0"""
        tan = abs((left_line.slope - right_line.slope) / (1 + left_line.slope * right_line.slope))
        return np.atan(tan)


def calc_reg_line(pt_lst, comm):
    """Given a list corresponding to points plotted on a vocal cord. Calculates
    a regression line from those points which is used to represent the cord."""
    pfx = []
    pfy = []
    for item in pt_lst:
        if item is not None:
            pfx.append(item[0])
            pfy.append(item[1])
    pf = stats.linregress(pfx, pfy)
    if comm and len(pfx) > 3:
        pfc = stats.linregress(pfx[1:], pfy[1:])
        if abs(pfc[2]) > abs(pf[2]):
            pf = pfc
    pfc = outlier_del(pfx, pfy, comm, pf)
    if abs(pfc[2]) > abs(pf[2]):
        pf = pfc
    if pf[2] ** 2 < 0.8:
        return None
    slope = pf[0]
    yint = pf[1]
    return Line(slope, yint)


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


def outlier_del(pfx, pfy, comm, pf):
    """Deletes outliers from sufficiently large cord lists."""
    if comm:
        pfx = pfx[1:]
        pfy = pfy[1:]
    if len(pfx) > 3:
        for i in range(len(pfx) - 1):
            newx = []
            newy = []
            for j in range(len(pfx)):
                newx.append(pfx[j])
                newy.append(pfy[j])
            newx.pop(i)
            newy.pop(i)
            newline = stats.linregress(newx, newy)
            if len(newx) > 3:
                newline = outlier_del(newx, newy, False, newline)
            if newline[2] > pf[2]:
                pf = newline
    return pf