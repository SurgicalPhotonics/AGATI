import numpy as np
from typing import List
from TrackingObjects import Point
from TrackingObjects import Line
from math import sqrt, atan

"""bp = List[Point]  # list of all marked parts presumably get with frame
left_cord = Line(bp[0], bp[7])
right_cord = Line(bp[13], bp[0])"""  # For copying into functions

error_const: int  # Multiplicative constant for angular velocity error.

"""bp[0] is the anterior commissure. bp[7] is left vocal process. bp[13] is 
right vocal process. Camera flips the image so patient's left is 
our right"""


def line_len(l: Line):
    """Returns length of input line"""
    return sqrt((l.end2.x - l.end1.x) ^ 2 + (l.end2.y - l.end1.y) ^ 2)


def partially_paralyzed(frames: list):
    for frame in frames:
        bp = List[Point]  # list of all marked parts presumably get with frame
        left_cord = Line(bp[0], bp[7])
        right_cord = Line(bp[13], bp[0])
        ref_line = Line(bp[0], bp[1])
        # line between anterior commissure and ref pt
        left_angle = atan(line_len(left_cord) / line_len(ref_line))
        right_angle = atan(line_len(right_cord) / line_len(ref_line))
        if not 1 / error_const * left_angle < right_angle < error_const * \
                left_angle:
            return True
    return False







