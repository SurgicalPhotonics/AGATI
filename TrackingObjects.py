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
        if isinstance(e1, tuple):
            if e1[0] > e2[0]:
                self.end1 = e2
                self.end2 = e1
            else:
                self.end1 = e1
                self.end2 = e2
            if not self.end2[0] == self.end1[0]:
                slope = (self.end2[1] - self.end1[1])/(self.end2[0] - self.end1
                [0])
            else:
                slope = 999999999999999
            self.slope = slope
            yint = e1[1] - slope * e1[0]
            self.yint = yint
        else:
            # If slope and yint passed directly
            self.slope = e1
            self.yint = e2
            self.end1 = (0, self.yint)
            self.end2 = (1, int(self.yint + self.slope))

    def set_ends(self, cord):
        """Allows a new end2 point to be passed from outside."""
        c = []
        for point in cord:
            if point is not None:
                c.append(point)
        y = c[len(c) - 1][1]
        if self.slope != 0:
            self.end2 = (int((y - self.yint) / self.slope), int(y))
        else:
            self.end2 = (1, int(y))
        y = c[0][1]
        if self.slope != 0:
            self.end1 = (int((y - self.yint) / self.slope), int(y))
        else:
            self.end1 = (1, int(y))
# Potential add parabolic approximation later.
