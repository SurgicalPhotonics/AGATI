import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from typing import List, Tuple
from TrackingObjects import Point
from TrackingObjects import Line
from math import sqrt, asin, acos, atan, pi
from DataReader import read_data

"""bp = List[Point]  # list of all marked parts presumably get with frame
left_cord = Line(bp[0], bp[7])
right_cord = Line(bp[13], bp[0])"""  # For copying into functions

par_const: int
# Multiplicative constant for angular position error.
deformation_const: int
# Comparative constant for observed vs expected point pos as line length


"""bp[0] is the anterior commissure. bp[7] is left vocal process. bp[13] is 
right vocal process. Camera flips the image so patient's left is 
our right"""


class Tracker:
    """Creates a tracker object that takes a dataset and can perform various
    calculations on it.
    data: lst[lst[float]]
    output: lst[tuple(float, float)]
    contains marked parts and their corresponding points at each frame.
    """

    def __init__(self, data):
        self.data = data

    def frame_by(self):
        """Goes through lists and returns all data for each frame."""
        ac1 = self.data[0]
        LC = [ac1, self.data[2], self.data[3], self.data[4], self.data[5],
              self.data[6], self.data[7]]
        RC = [ac1, self.data[8], self.data[9], self.data[10], self.data[11],
              self.data[12], self.data[13]]
        graph = []
        for i in range(len(self.data[1])):
            if not ac1[i][2] == 0:  # and not ac2[i][2] == 0:
                ac1pt = Point(ac1[i][0], ac1[i][1])
                # ac2pt = Point(ac2[i][0], ac2[i][1])
                LC_now = []
                RC_now = []
                cords_there = False
                for j in range(len(LC)):
                    LC_now.append(LC[j][i])
                    RC_now.append(RC[j][i])
                    if LC[j][i][0] != 0 or RC[j][i][0] != 0 and len(LC_now) > 2\
                            and len(RC_now) > 2:
                        cords_there = True
                if cords_there:
                    # midline = Line(ac1pt, ac2pt)  # This will change
                    # angle = angle_from_midline(midline, ac1pt, LC_now, RC_now)
                    angle = angle_of_opening(LC_now, RC_now)
                    # if angle[0] < pi and angle[1] < pi:
                    if angle < pi:
                        graph.append(angle)
        # lgraph = []
        # rgraph = []
        dgraph = []
        for item in graph:
            # lgraph.append(item[0] * 360 / (2 * pi))
            # rgraph.append(item[1] * 360 / (2 * pi))
            dgraph.append(item * 360 / (2 * pi))
        arr = np.array(dgraph)
        print(np.mean(arr))
        print(np.std(arr))
        print(np.max(arr))
        print(np.max(arr) - np.min(arr))
        print(np.percentile(arr, 99.9))
        k = plt.figure(4)
        plt.title('Angle of Opening')
        plt.plot(dgraph)
        plt.xlabel('Frames')
        plt.ylabel('Angle Between Cords')
        plt.show()


def line_len(l):
    """Returns length of input line"""
    return sqrt((l.end2.x - l.end1.x) ** 2 + (l.end2.y - l.end1.y) ** 2)


def shortest_distance(p, l):
    """Returns shortest distance between line and point"""
    return abs(-l.slope * p.x + p.y - l.yint) / sqrt(l.slope ** 2 + 1)


def calc_reg_line(pt_lst):
    """Returns a regression line based on the points in pt_lst. Should only take
    individual frame of AC not entire set. This doesn't work if the line is
    perfectly vertical, but programming an exception case would increase compute
    time for all cases, which is not worth doing for something so unlikely."""
    pfx = []
    pfy = []
    for item in pt_lst:
        pfx.append(item[0])
        pfy.append(item[1])
    pf = stats.linregress(pfx, pfy)
    if abs(pf[2]) < .8:
        return Line(0, 0)
    slope = pf[0]
    yint = pf[1]
    return Line(slope, yint)


def angle_from_midline(midline, ac1, left_cord, right_cord):
    """Uses midline defined by points around anterior commissure to
    approximate angle of opening on each side."""
    top_left_num = left_cord[len(left_cord) - 1]
    top_left = Point(top_left_num[0], top_left_num[1])
    top_right_num = right_cord[len(right_cord) - 1]
    top_right = Point(top_right_num[0], top_right_num[1])
    left_line = Line(ac1, top_left)
    right_line = Line(ac1, top_right)
    left_opp = shortest_distance(top_left, midline)
    right_opp = shortest_distance(top_right, midline)
    lsin = left_opp / line_len(left_line)
    rsin = right_opp / line_len(right_line)
    if lsin > 1 or rsin > 1:
        return pi, pi
    return asin(lsin), asin(rsin)


def angle_of_opening(left_cord, right_cord):
    """Calculates angle of opening between left and right cord."""
    """top_left_num = left_cord[len(left_cord) - 1]
    top_left = Point(top_left_num[0], top_left_num[1])
    top_right_num = right_cord[len(right_cord) - 1]
    top_right = Point(top_right_num[0], top_right_num[1])
    left_line = Line(ac1, top_left)
    right_line = Line(ac1, top_right)
    top_line = Line(top_right, top_left)
    cos = (line_len(left_line) ** 2 + line_len(right_line) ** 2 - line_len
    (top_line) ** 2) / (2 * line_len(left_line) * line_len(right_line))
    if cos > 1:
        return pi
    else:
        return acos(cos)"""
    """i = 1
    while i < len(left_cord):
        if left_cord[i][0] - left_cord[i-1][0] < -2:
            left_cord.pop(i)
        else:
            i += 1
    i = 1
    while i < len(right_cord):
        if right_cord[i][0] - right_cord[i-1][0] > 2:
            right_cord.pop(i)
        else:
            i += 1"""
    left_line = calc_reg_line(left_cord)
    right_line = calc_reg_line(right_cord)
    if left_line.slope == 0 or right_line.slope == 0:
        return pi
    tan = abs((left_line.slope - right_line.slope) / (1 + left_line.slope *
                                                      right_line.slope))
    return atan(tan)


if __name__ == '__main__':
    data = read_data('vocal3DeepCut_resnet50_vocalMay13shuffle1_1030000.h5')
    t = Tracker(data)
    t.frame_by()
