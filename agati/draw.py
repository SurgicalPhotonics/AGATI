import cv2
import os
import numpy as np
from tqdm import tqdm


def point0(line: "np.ndarray") -> (int, int):
    return int(line[2]), int(line[3])


def point1(line: "np.ndarray"):
    return int(line[4]), int(line[5])


def draw(
    video_path: str,
    midlines: "np.ndarray",
    true_lines_l: "np.ndarray",
    true_lines_r: "np.ndarray",
    false_lines_l: np.ndarray,
    false_lines_r: np.ndarray,
    aeg_line_l,
    aeg_line_r,
    angles: "np.ndarray",
    outfile: str = None,
    video_type: str = ".mp4",
):
    """

    :param video_path:
    :param midlines:
    :param true_lines_l:
    :param true_lines_r:
    :param false_lines_l:
    :param false_lines_r:
    :param aeg_line_l:
    :param aeg_line_r:
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
    print(f"Printing lines on {os.path.split(video_path)[1]} in {os.path.split(outfile)[1]}")
    for i in tqdm(range(frames)):
        true_l = true_lines_l[i]
        true_r = true_lines_r[i]
        if not np.isnan(true_l).any() and not np.isnan(true_r).any():
            cross = intersect(true_l, true_r)
        else:
            cross = None
        if not np.isnan(midlines[i]).any():
            cv2.line(im, point0(midlines[i]), point1(midlines[i]), (255, 0, 0), 2)
        if not np.isnan(true_l).any() and not np.isnan(true_r).any():
            cv2.line(im, point0(true_l), point1(true_l), (0, 0, 255), 2)
            cv2.line(im, point0(true_r), point1(true_r), (0, 255, 0), 2)
        elif cross is not None:
            if (
                cross[1] > (true_l[3] + true_r[3]) / 2 + 20
                or cross[1] < (true_l[3] + true_r[3]) / 2 - 20
            ):
                cv2.line(im, point0(true_l), point1(true_l), (0, 0, 255), 2)
                cv2.line(im, point0(true_r), point1(true_r), (0, 255, 0), 2)
            else:
                cv2.line(im, cross, point1(true_l), (255, 0, 0), 2)
                cv2.line(im, cross, point1(true_r), (255, 0, 0), 2)
        if not np.isnan(false_lines_l[i]).any() and not np.isnan(false_lines_r[i]).any():
            cv2.line(im, point0(false_lines_l[i]), point1(false_lines_l[i]), (0, 0, 255), 2)
            cv2.line(im, point0(false_lines_r[i]), point1(false_lines_r[i]), (0, 255, 0), 2)
        if not np.isnan(aeg_line_l).any and not np.isnan(aeg_line_l).any():
            cv2.line(im, point0(aeg_line_l[i]), point1(aeg_line_l[i]), (0, 0, 255), 2)
            cv2.line(im, point0(aeg_line_r[i]), point1(aeg_line_r[i]), (0, 255, 0), 2)

        if not np.isnan(angles[i]).any():
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


def intersect(left_line: "np.ndarray", right_line: "np.ndarray") -> (int, int):
    """Returns the point of intersection of two lines. Used to define anterior
    commissure from which to start lines."""
    a1 = left_line[2:4]
    a2 = left_line[4:6]
    b1 = right_line[2:4]
    b2 = right_line[4:6]
    s = np.vstack([a1, a2, b1, b2])  # s for stacked
    h = np.hstack((s, np.ones((4, 1))))  # h for homogeneous
    l1 = np.cross(h[0], h[1])  # get first line
    l2 = np.cross(h[2], h[3])  # get second line
    x, y, z = np.cross(l1, l2)  # point of intersection
    if z == 0:  # lines are parallel
        return np.nan
    return int(x / z), int(y / z)
