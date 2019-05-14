import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from TrackingObjects import Point
from TrackingObjects import Line
from math import sqrt, asin, pi
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
        ac2 = self.data[1]
        LC = [self.data[2], self.data[3], self.data[4], self.data[5],
              self.data[6], self.data[7]]
        RC = [self.data[8], self.data[9], self.data[10], self.data[11],
              self.data[12], self.data[13]]
        graph = []
        temp = []
        for i in range(len(self.data[1])):
            if not ac1[i][0] == 0 and not ac2[i] == 0:
                ac1pt = Point(ac1[i][0], ac1[i][1])
                ac2pt = Point(ac2[i][0], ac2[i][1])
                LC_now = []
                RC_now = []
                cords_there = False
                for j in range(len(LC) - 1):
                    LC_now.append(LC[j][i])
                    RC_now.append(RC[j][i])
                    if LC[j][i][0] != 0 or RC[j][i][0] != 0:
                        cords_there = True
                if cords_there:
                    angle = angle_of_opening(ac1pt, ac2pt, LC_now, RC_now)
                    if angle[0] < pi and angle[1] < pi:
                        graph.append(angle)
                    else:
                        temp.append(angle)
        lgraph = []
        rgraph = []
        for item in graph:
            lgraph.append(item[0])
            rgraph.append(item[1])
        ind = [i for i in range(len(lgraph))]
        xlab = 'Frames (could be innacurate depending on quality of video and '\
               'training'
        ylab = 'Angle from midline'
        f = plt.figure(1)
        plt.plot(ind, lgraph)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        g = plt.figure(2)
        plt.plot(ind, rgraph)
        plt.xlabel(xlab)
        plt.ylabel(ylab)
        plt.show()


def line_len(l: Line):
    """Returns length of input line"""
    return sqrt((l.end2.x - l.end1.x) ** 2 + (l.end2.y - l.end1.y) ** 2)


def shortest_distance(p, l):
    """Returns shortest distance between line and point"""
    return abs((l.slope * p.x + -1 * p.y + l.yint)) / (sqrt(l.slope * l.slope +
                                                            1))


def angle_of_opening(ac1, ac2, left_cord, right_cord):
    """Uses midline defined by points around anterior commissure to
    approximate angle of opening on each side."""
    midline = Line(ac1, ac2)
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


if __name__ == '__main__':
    data = read_data('vocal1DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5')
    t = Tracker(data)
    t.frame_by()
    print('something')






