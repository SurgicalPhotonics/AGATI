import cv2
import os
import numpy as np
from tqdm import tqdm
from typing import List
from dlc_generic_analysis.geometries import Line


def draw(
    video_path: str,
    left: "List[Line]",
    right: "List[Line]",
    angles: "np.ndarray",
    outfile: str = None,
    video_type: str = ".mp4",
):
    """
    Takes each frame from video and stitches it back into new video with
    line drawn on.
    :param video_path:
    :param left:
    :param right:
    :param angles:
    :param outfile:
    :param video_type:
    :return:
    """
    print("Printing Lines on Videos")
    raw_video = cv2.VideoCapture(video_path)
    frame_rate = raw_video.get(cv2.CAP_PROP_FPS)
    width = int(raw_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(raw_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames = int(raw_video.get(cv2.CAP_PROP_FRAME_COUNT))
    if outfile is None:
        file, ext = os.path.splitext(video_path)
        outfile = file + "_analyzed" + ext
    s, im = raw_video.read()
    if video_type is None:
        video_type = os.path.splitext(video_path)[1]
    if video_type == ".mp4":
        fourcc = cv2.VideoWriter.fourcc("m", "p", "4", "v")
    elif video_type == ".avi":
        fourcc = cv2.VideoWriter.fourcc("x", "v", "i", "d")
    else:
        fourcc = 0
    w = cv2.VideoWriter(outfile, fourcc, frame_rate, (width, height))
    print(f"Printing lines on {os.path.split(video_path)[1]}")
    for i in tqdm(range(frames)):
        left_line = left[i]
        right_line = right[i]
        if left_line is not None and right_line is not None:
            cross = intersect(left_line, right_line)
        else:
            cross = None
        if (
            left_line is not None
            and right_line is not None
            and left_line.slope > 10
            and right_line.slope > 10
        ):
            cv2.line(im, left_line.end1, left_line.end2, (255, 0, 0), 2)
            cv2.line(im, right_line.end1, right_line.end2, (255, 0, 0), 2)
        elif cross is not None:
            if (
                cross[1] > (left_line.end1[1] + right_line.end1[1]) / 2 + 20
                or cross[1] < (left_line.end1[1] + right_line.end1[1]) / 2 - 20
            ):
                cv2.line(im, left_line.end1, left_line.end2, (255, 0, 0), 2)
                cv2.line(im, right_line.end1, right_line.end2, (255, 0, 0), 2)
            else:
                cv2.line(im, cross, left_line.end2, (255, 0, 0), 2)
                cv2.line(im, cross, right_line.end2, (255, 0, 0), 2)
        if not np.isnan(angles[i]):
            cv2.putText(
                im,
                str(round(angles[i], 2)),
                (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (1, 1, 198),
                2,
                cv2.LINE_AA,
            )
        w.write(im)
        s, im = raw_video.read()
        if not s:
            break
    raw_video.release()
    w.release()
    print("Video writing finished")
    return os.path.join(video_path[: video_path.rfind("videos")], video_path)


def intersect(left_line: Line, right_line: Line) -> (int, int):
    """Returns the point of intersection of two lines. Used to define anterior
    commissure from which to start lines."""
    a1 = left_line.end1
    a2 = left_line.end2
    b1 = right_line.end1
    b2 = right_line.end2
    s = np.vstack([a1, a2, b1, b2])  # s for stacked
    h = np.hstack((s, np.ones((4, 1))))  # h for homogeneous
    l1 = np.cross(h[0], h[1])  # get first line
    l2 = np.cross(h[2], h[3])  # get second line
    x, y, z = np.cross(l1, l2)  # point of intersection
    if z == 0:  # lines are parallel
        return None
    return int(x / z), int(y / z)
