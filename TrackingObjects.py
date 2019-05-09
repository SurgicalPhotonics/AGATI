class Point:
    """A point in the video frame represents any given 'body part' as DLC calls
    them. Only properties are x and y coordinates.
    x: float
        x coordinate
    y: float
        y coordinate
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    """A line between two points. Used to measure scarring or other deformation
    in vocal cords.
    eq: Str
        Equation of line. We compare points in LC and RC to their
        respective lines to check for deformation
    end1: point
        first endpoint of the line. Endpoint with smaller x value if x1 \neq x2
    end2: point
        second endpoint of the line. Endpoint with greater x if x1 \neq x2
    """
    def __init__(self, e1, e2):
        self.end1 = e1
        self.end2 = e2
        slope = (e2.x - e1.x)/(e2.y - e1.y)
        yint = e1.y + slope * e1.x
        self.eq = slope + 'x' + '+' + yint

# Potential add parabolic approximation later.
