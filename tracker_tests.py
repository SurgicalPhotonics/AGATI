import tracker
import pytest
from TrackingObjects import Point
from math import pi, sqrt


def test_angle_calc():
    """Tests that the basic calculations in angle_of_opening() work correctly"""
    ac1 = Point(1, 0)
    ac2 = Point(2, -1/(sqrt(2) - 1))
    angle = tracker.angle_of_opening(ac1, ac2, [(1, sqrt(2))], [(0, 1)])
    assert angle[0] == pytest.approx(pi / 8) == angle[1]


if __name__ == '__main__':
    pytest.main(['tracker_tests.py'])
