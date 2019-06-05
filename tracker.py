import numpy as np
import matplotlib.pyplot as plt
from draw import draw, intersect
from scipy import stats
from TrackingObjects import Line
from math import atan, pi
from DataReader import read_data


class Tracker:
    """Creates a tracker object that takes a dataset and can perform various
    calculations on it.
    data: lst[lst[float]]
    output: lst[tuple(float, float)]
    contains marked parts and their corresponding points at each frame.
    """

    def __init__(self, data):
        self.data = data
        self.left = []
        self.right = []

    def frame_by(self, path):
        """Goes through each frame worth of data. Analyses and graphs opening
        angle of vocal cords. Prints summary statistics."""
        ac1 = self.data[0]
        # frames dropped
        i = 0
        for item in self.data[1]:
            if item is not None:
                i += 1
        print(i)
        LC = [ac1, self.data[1], self.data[2], self.data[3], self.data[4],
              self.data[5], self.data[6]]
        RC = [ac1, self.data[7], self.data[8], self.data[9], self.data[10],
              self.data[11], self.data[12]]
        graph = []
        for i in range(len(self.data[1])):
            LC_now = []
            RC_now = []
            cords_there = False
            comm = False
            for j in range(len(LC)):
                if LC[j][i] is not None:
                    LC_now.append(LC[j][i])
                    if j == 0:
                        comm = True
                    cords_there = True
            for j in range(len(RC)):
                if RC[j][i] is not None:
                    RC_now.append(RC[j][i])
                    cords_there = True
            num_pts = 0  # number of legitimate points on a cord
            for item in LC_now:
                if item is not None:
                    num_pts += 1
            if num_pts < 3:
                cords_there = False
            num_pts = 0
            for item in RC_now:
                if item is not None:
                    num_pts += 1
            if num_pts < 3:
                cords_there = False
            if cords_there:
                angle = self.angle_of_opening(LC_now, RC_now, comm)
                graph.append(angle)
            else:
                self.left.append(None)
                self.right.append(None)
                graph.append(None)
        dgraph = []  # keep none to show blank space in graph.
        sgraph = []  # remove none to perform statistical analysis.
        for item in graph:
            if item is not None:
                dgraph.append(item * 180 / pi)
                sgraph.append(item * 180 / pi)
            else:
                dgraph.append(None)
        arr = np.array(sgraph)
        print(i)
        print('Mean: ')
        print(np.mean(arr))
        print('Std Dev: ')
        print(np.std(arr))
        print('Max: ')
        print(np.max(arr))
        print('Range: ')
        print(np.max(arr) - np.min(arr))
        print('99th: ')
        print(np.percentile(arr, 97))
        print('Min: ')
        print(np.min(arr))
        print(len(data[1]) == len(dgraph))
        plt.title('Angle of Opening at Anterior Commissure')
        plt.plot(dgraph)
        plt.xlabel('Frames')
        plt.ylabel('Angle Between Cords')
        print(len(dgraph))
        draw(path, (self.left, self.right), dgraph)
        print('Video made')
        plt.show()

    def angle_of_opening(self, left_cord, right_cord, comm):
        """Calculates angle of opening between left and right cord."""
        left_line = calc_reg_line(left_cord, comm)
        right_line = calc_reg_line(right_cord, comm)
        left_plot = calc_print_line(left_cord)
        right_plot = calc_print_line(right_cord)
        self.left.append(left_plot)
        self.right.append(right_plot)
        if left_plot is not None and right_plot is not None:
            left_plot.set_ends(left_cord)
            right_plot.set_ends(right_cord)
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
        tan = abs((left_line.slope - right_line.slope) / (1 + left_line.slope *
                                                          right_line.slope))
        return atan(tan)


def calc_reg_line(pt_lst, comm):
    """Given a list corresponding to points plotted on a vocal cord. Calculates
    a regression line from those points which is used to represent the cord."""
    pfx = []
    pfy = []
    for item in pt_lst:
        pfx.append(item[0])
        pfy.append(item[1])
    pf = stats.linregress(pfx, pfy)
    if comm and len(pfx) > 3:
        pfc = stats.linregress(pfx[1:], pfy[1:])
        if pfc[2] ** 2 > pf[2] ** 2:
            pf = pfc
        if 3 < len(pfx):
            pf = pfc
    pf = outlier_del(pfx, pfy, comm, pf)
    if pf[2] ** 2 < .8:
        return None
    slope = pf[0]
    yint = pf[1]
    return Line(slope, yint)


def calc_print_line(pt_lst):
    """Given a list corresponding to points plotted on a vocal cord. Calculates
    a regression line from those points which is used to represent the cord."""
    pfx = []
    pfy = []
    for item in pt_lst:
        pfx.append(item[0])
        pfy.append(item[1])
    pf = stats.linregress(pfx, pfy)
    if pf[2] ** 2 < .5:
        return None
    slope = pf[0]
    yint = pf[1]
    return Line(slope, yint)


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
            if newline[2] ** 2 > pf[2] ** 2:
                pf = newline
    return pf


if __name__ == '__main__':
    data = read_data('vocalDeepCut_resnet50_vocal_paperMay23shuffle1_900000.h5')
    #data = read_data('uvfp1DeepCut_resnet50_vocal_paperMay23shuffle1_900000.h5')
    t = Tracker(data)
    t.frame_by('vocalDeepCut_resnet50_vocal_paperMay23shuffle1_900000_labeled.mp4')
    #t.frame_by('uvfp1DeepCut_resnet50_vocal_paperMay23shuffle1_900000_labeled.mp4')
