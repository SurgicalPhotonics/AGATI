import tracker
import pytest
from TrackingObjects import Point, Line
from math import pi, sqrt


def test_angle_calc():
    """Tests that the basic calculations in angle_of_opening() work correctly"""
    ac1 = Point(1, 0)
    ac2 = Point(2, -1 / (sqrt(2) - 1))
    midline = Line(ac1, ac2)
    angle = tracker.angle_of_opening(midline, ac1, [(1, sqrt(2))], [(0, 1)])
    assert angle[0] == pytest.approx(pi / 8) == angle[1]


def test_same_angle_hard_pt():
    """Tests that angle calculations work for same angles with different points
    as input."""
    ac1 = Point(1, 0)
    ac2 = Point(2, -1 / (sqrt(2) - 1))
    midline = Line(ac1, ac2)
    angle = tracker.angle_of_opening(midline, ac1, [(1, 5)], [(0, 1)])
    assert angle[0] == pytest.approx(pi / 8) == angle[1]


def test_different_cord_angles():
    """Tests to see that calculations are correct for asymmetrical cords"""
    ac1 = Point(1, 0)
    ac2 = Point(2, -1 / (sqrt(2)-1))
    midline = Line(ac1, ac2)
    angle = tracker.angle_of_opening(midline, ac1, [(1.892, 1.784)], [(0, 1)])
    assert angle[1] == pytest.approx(pi / 8)
    assert angle[0] == pytest.approx(0.8563466906995302)


def test_make_midline():
    """Tests that midlines are computed correctly for different data."""
    ac_lst = [(3, 2, 1), (2.99, 1, 1), (2.9, 12, 1)]
    l = tracker.calc_midline(ac_lst)
    assert l.slope < -100
    ac_inf = [(3, 2, 1), (3, 1, 1), (3.000001, 15, 1)]
    m = tracker.calc_midline(ac_inf)
    assert m.slope > 1000


def test_midline_real_data():
    """Tests midline on data from early dlc output file."""
    # We'll implement this once we have dlc back up and running on the desktop.
    pass


if __name__ == '__main__':
    pytest.main(['tracker_tests.py'])
