import deeplabcut as dlc
import cv2


def downsample(path):
    """Downsamples high res videos"""
    cap = cv2.VideoCapture(path)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if height <= 480:
        print('Already proper resolution')
        return path
    else:
        print('Downsampling to more fitting resolution')
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frames = cap.get(cv2.CAP_PROP_FPS)
        r_height = 360
        ar = width / height
        r_width = int(ar * 360)
        fourcc = cv2.VideoWriter.fourcc('m', 'p', '4', 'v')
        name = path[:path.rfind('.')] + '_resized.mp4'
        writer = cv2.VideoWriter(name, fourcc, frames, (r_width, r_height))
        s, im = cap.read()
        while s:
            image = cv2.resize(im, (r_width, r_height))
            writer.write(image)
            s, im = cap.read()
        return name


if __name__ == '__main__':
    path = downsample(r'C:\Users\natad\Downloads\Barrel Distortion Correction\nop15corr.mp4')
    dlc.create_labeled_video(r'vocal_fold-Nat-2019-08-07\config.yaml',
                             [path], videotype='.mp4')
