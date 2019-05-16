import tracker
import pytest
from TrackingObjects import Point
from math import pi, sqrt


def test_angle_calc():
    """Tests that the basic calculations in angle_of_opening() work correctly"""
    ac1 = Point(1, 0)
    ac2 = Point(2, -1 / (sqrt(2) - 1))
    angle = tracker.angle_of_opening(ac1, ac2, [(1, sqrt(2))], [(0, 1)])
    assert angle[0] == pytest.approx(pi / 8) == angle[1]


def test_same_angle_hard_pt():
    """Tests that angle calculations work for same angles with different points
    as input."""
    ac1 = Point(1, 0)
    ac2 = Point(2, -1 / (sqrt(2) - 1))
    angle = tracker.angle_of_opening(ac1, ac2, [(1, 5)], [(0, 1)])
    assert angle[0] == pytest.approx(pi / 8) == angle[1]


def test_different_cord_angles():
    """Tests to see that calculations are correct for asymmetrical cords"""
    ac1 = Point(1, 0)
    ac2 = Point(2, -1 / (sqrt(2)-1))
    angle = tracker.angle_of_opening(ac1, ac2, [(1.892, 1.784)], [(0, 1)])
    assert angle[1] == pytest.approx(pi / 8)
    assert angle[0] == pytest.approx(0.8563466906995302)


if __name__ == '__main__':
    pytest.main(['tracker_tests.py'])
