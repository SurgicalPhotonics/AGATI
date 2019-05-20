import cv2
# This is basically just notes at this point, also might go back into other file


def draw(img, midline, ac1, height):
    """Draws lines on frames of video. Height = window.GetMaxHeight"""
    pt1 = ((ac1.y - midline.yint) / midline.slope, 0)
    pt2 = ((height - midline.yint) / midline.slope, height)
    return cv2.line(img, pt1, pt2, (255, 0, 0), 3)

