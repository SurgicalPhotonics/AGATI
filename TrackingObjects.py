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
    end1: point
        first point to calc line Endpoint with smaller x value if x1 \neq x2
    end2: point
        second point to calc line. Endpoint with greater x if x1 \neq x2
    slope: float
        slope of the line
    yint: float
        y intercept of line
    """
    def __init__(self, e1, e2):
        if e1.x > e2.x:
            self.end1 = e2
            self.end2 = e1
        else:
            self.end1 = e1
            self.end2 = e2
        slope = (self.end2.y - self.end1.y)/(self.end2.x - self.end1.x)
        self.slope = slope
        yint = e1.y + slope * e1.x
        self.yint = yint

# Potential add parabolic approximation later.
