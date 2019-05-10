import numpy as np
from typing import List
from TrackingObjects import Point
from TrackingObjects import Line
from math import sqrt, asin

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


def line_len(l: Line):
    """Returns length of input line"""
    return sqrt((l.end2.x - l.end1.x) ^ 2 + (l.end2.y - l.end1.y) ^ 2)


def shortest_distance(p, l):
    """Returns shortest distance between line and point"""
    return abs((l.slope * p.x + -1 * p.y + l.yint)) / (sqrt(l.slope * l.slope
                                                            + 1))

def angle_of_opening(ac1, ac2, left_cord, right_cord):
    """Uses midline defined by points around anterior commissure to approximate
    angle of opening on each side."""
    midline = Line(ac1, ac2)
    top_left = left_cord[len(left_cord)]
    top_right = right_cord[len(right_cord)]
    left_line = Line(ac1, top_left)
    right_line = Line(ac1, top_right)
    left_opp = shortest_distance(top_left, midline)
    right_opp = shortest_distance(top_right, midline)
    return [asin(left_opp / line_len(left_line)), asin(right_opp /
                                                       line_len(right_line))]


def cord_deformity(frames: list):
    """Checks that patient's vocal cords are approximately linear"""
    for frame in frames:
        bp = List[Point]  # list of all marked parts presumably get with frame
        left_cord = Line(bp[0], bp[7])
        right_cord = Line(bp[13], bp[0])
        lc = bp[0]
        lc.extend(bp[2:7])
        rc = bp[0]
        rc.extend(bp[8:13])
        for point in lc:
            # Check that distance is less than constant






