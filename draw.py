from cv2 import VideoCapture, CAP_PROP_FPS, CAP_PROP_FRAME_WIDTH, CAP_PROP_FRAME_HEIGHT, VideoWriter, line, putText, destroyAllWindows, FONT_HERSHEY_SIMPLEX, LINE_AA
from os import path as ospath
from numpy import cross as npcross, vstack, hstack, ones


def draw(path, lines, angles, outfile, videotype='.mp4'):
    """Takes each frame from video and stitches it back into new video with
    line drawn on."""
    print("Printing Lines on Videos")
    cap = VideoCapture(path)
    frames = cap.get(CAP_PROP_FPS)
    width = int(cap.get(CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(CAP_PROP_FRAME_HEIGHT))
    s, im = cap.read()
    count = 0
    name = path[path.rfind('\\') + 1:path.rfind('.')] + 'with_lines'
    if videotype == '.mp4':
        fourcc = VideoWriter.fourcc('m', 'p', '4', 'v')
    elif videotype == '.avi':
        fourcc = VideoWriter.fourcc('x', 'v', 'i', 'd')
    else:
        fourcc = 0
    out = ospath.join(outfile, name + videotype)
    w = VideoWriter(out, fourcc, frames, (width, height))
    print('Printing lines on your video.')
    while s:
        if count % 5 == 0:
            print(str(round(count / len(angles) * 100)) + '%')
        left_line = lines[0][count]
        right_line = lines[1][count]
        if left_line is not None and right_line is not None:
            cross = intersect(left_line, right_line)
        else:
            cross = None
        if left_line is not None and right_line is not None and left_line.slope > 10 and right_line.slope > 10:
            line(im, left_line.end1, left_line.end2, (255, 0, 0), 2)
            line(im, right_line.end1, right_line.end2, (255, 0, 0), 2)
        elif cross is not None:
            if cross[1] > (left_line.end1[1] + right_line.end1[1]) / 2 + 20 or cross[1] < (left_line.end1[1] + right_line.end1[1]) / 2 - 20:
                line(im, left_line.end1, left_line.end2, (255, 0, 0), 2)
                line(im, right_line.end1, right_line.end2, (255, 0, 0), 2)
            else:
                line(im, cross, left_line.end2, (255, 0, 0), 2)
                line(im, cross, right_line.end2, (255, 0, 0), 2)
        if angles[count] is not None:
            putText(im, str(round(angles[count][0], 2)), (10, 20), FONT_HERSHEY_SIMPLEX, 1,  (1, 1, 198), 2, LINE_AA)
        w.write(im)
        s, im = cap.read()
        count += 1
    cap.release()
    w.release()
    # destroyAllWindows()
    return ospath.join(path[:path.rfind('videos')], name)


def intersect(left_line, right_line):
    """Returns the point of intersection of two lines. Used to define anterior
    commissure from which to start lines."""
    a1 = left_line.end1
    a2 = left_line.end2
    b1 = right_line.end1
    b2 = right_line.end2
    s = vstack([a1, a2, b1, b2])  # s for stacked
    h = hstack((s, ones((4, 1))))  # h for homogeneous
    l1 = npcross(h[0], h[1])  # get first line
    l2 = npcross(h[2], h[3])  # get second line
    x, y, z = npcross(l1, l2)  # point of intersection
    if z == 0:  # lines are parallel
        return None
    return int(x / z), int(y / z)
