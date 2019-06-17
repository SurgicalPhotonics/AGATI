import deeplabcut as dlc
import os

VID_NUM = 10
# Only works on windows rn


# might change how we handle pathing
def new_vid(config, path):
    """Adds new video to project"""
    #cfg = r'' + os.path.join(config, 'config.yaml')
    cfg = r'C:\Users\natad\PycharmProjects\VCTrack\vocal-Nat-2019-06-10\config.yaml'
    path = r'' + path
    dlc.add_new_videos(cfg, [path])
    location = os.path.join('videos\\' + path[path.rfind('/') + 1:])
    test = r'' + os.path.join(config, location)
    videotype = path[path.rfind('.'):]
    dlc.analyze_videos(cfg, [test], videotype=videotype)


def analyze(config, path):
    """Analyzes new video"""
    cfg = os.path.join(config, 'config.yaml')
    dlc.analyze_videos(cfg, [path], videotype=path[path.last('.') - 1:])
    conf = dlc.auxiliaryfunctions.read_config(cfg)
    new_vid = conf['video_sets'][VID_NUM]
    h5 = new_vid[0: new_vid.last('.')] + '.h5'
    return h5


def label(config, path):
    """Creates labeled video from new video"""
    cfg = os.path.join(config, 'config.yaml')
    dlc.create_labeled_video(cfg, [path], videotype=path[path.last('.') - 1:])
    conf = dlc.auxiliaryfunctions.read_config(cfg)
    new_vid = conf['video_sets'][VID_NUM]
    # Test when up and running. Might not return what we expect
    return new_vid


if __name__ == '__main__':
    pass
