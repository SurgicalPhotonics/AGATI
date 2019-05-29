import cv2
import os
import numpy as np


def draw(path, lines, frames=30, videotype='.mp4'):
    """Takes each frame from video and stitches it back into new video with
    line drawn on."""
    cap = cv2.VideoCapture(path)
    s, im = cap.read()
    count = 0
    new_path = os.path.join(path[:path.find('.')], 'lines' + videotype)
    fourcc = cv2.VideoWriter.fourcc(*'MP4V')
    w = cv2.VideoWriter(new_path, fourcc, frames, (640, 480))
    while s:
        left_line = lines[0][count]
        right_line = lines[1][count]
        cross = intersect(left_line, right_line)
        cv2.imwrite(path, cv2.line(im, cross, left_line.end2, (255, 0, 0), 3))
        w.write(im)
        cv2.imwrite(path, cv2.line(im, cross, right_line.end2, (255, 0, 0), 3))
        w.write(im)
        s, im = cap.read()
        count += 1
    w.release()


def intersect(left_line, right_line):
    """Returns the point of intersection of two lines. Used to define anterior
    commissure from which to start lines."""
    a1 = left_line.x
    a2 = left_line.y
    b1 = right_line.x
    b2 = right_line.y
    s = np.vstack([a1, a2, b1, b2])  # s for stacked
    h = np.hstack((s, np.ones((4, 1))))  # h for homogeneous
    l1 = np.cross(h[0], h[1])  # get first line
    l2 = np.cross(h[2], h[3])  # get second line
    x, y, z = np.cross(l1, l2)  # point of intersection
    if z == 0:  # lines are parallel
        return float('inf'), float('inf')
    return x / z, y / z



