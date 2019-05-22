import cv2
# This is basically just notes at this point, also might go back into other file
VID_FR = 30


def draw(path, midline, ac1, height):
    cap = cv2.VideoCapture(path)
    s, im = cap.read()
    count = 0
    w = cv2.VideoWriter(path, VID_FR)
    # New path
    while s:
        cv2.imwrite(path, dline(im, midline, ac1, height))
        w.write(im)
        s, im = cap.read()
        count += 1
    w.release()


def dline(img, midline, ac1, height):
    """Draws lines on frames of video. Height = window.GetMaxHeight"""
    pt1 = ((ac1.y - midline.yint) / midline.slope, 0)
    pt2 = ((height - midline.yint) / midline.slope, height)
    return cv2.line(img, pt1, pt2, (255, 0, 0), 3)



