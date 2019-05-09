import numpy as np
from typing import List
from TrackingObjects import Point
from TrackingObjects import Line
from math import sqrt, atan

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


def shortest_distance(x1, y1, a, b, c):
    """Returns shortest distance between line and point"""
    return abs((a * x1 + b * y1 + c)) / (sqrt(a * a + b * b))


def partially_paralyzed(frames: list):
    """Checks to see if one of the patient's vocal cords is paralyzed"""
    for frame in frames:
        bp = List[Point]  # list of all marked parts presumably get with frame
        left_cord = Line(bp[0], bp[7])
        right_cord = Line(bp[13], bp[0])
        ref_line = Line(bp[0], bp[1])
        # line between anterior commissure and ref pt
        left_angle = atan(line_len(left_cord) / line_len(ref_line))
        right_angle = atan(line_len(right_cord) / line_len(ref_line))
        if not 1 / par_const * left_angle < right_angle < par_const * \
                left_angle:
            return True
    return False


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
            #  Check that distance is less than constant






