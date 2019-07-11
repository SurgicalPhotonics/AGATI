import deeplabcut as dlc
import os

VID_NUM = 10
FILE_STRING = 'DeepCut_resnet50_vocalJun10shuffle1_1030000'
# Only works on windows rn


# might change how we handle pathing
def new_vid(config, path):
    """Adds new video to project"""
    cfg = r'' + os.path.join(config, 'config.yaml')
    path = r'' + path
    dlc.add_new_videos(cfg, [path])
    location = os.path.join('videos\\', path[path.rfind('/') + 1:])
    test = r'' + os.path.join(config, location)
    videotype = path[path.rfind('.'):]
    dlc.analyze_videos(cfg, [test], videotype=videotype)
    return os.path.join(config, location)


def analyze(config, path):
    """Analyzes new video"""
    cfg = os.path.join(config, 'config.yaml')
    dlc.analyze_videos(cfg, [path], videotype=path[path.rfind('.'):])
    location = os.path.join('videos\\', path[path.rfind('/') + 1:])
    new_vid = os.path.join(config, location)
    h5 = new_vid[0: new_vid.rfind('.')] + FILE_STRING + '.h5'
    return h5


def label(config, path):
    """Creates labeled video from new video"""
    cfg = os.path.join(config, 'config.yaml')
    location = os.path.join('videos\\', path[path.rfind('/') + 1:])
    vpath = os.path.join(config, location)
    dlc.create_labeled_video(cfg, [vpath], videotype=path[path.rfind('.'):])
    new_vid = os.path.join(config, location[:location.rfind('.')])
    vid = new_vid + FILE_STRING + '_labeled' + path[path.rfind('.'):]
    # Test when up and running. Might not return what we expect
    return vid


if __name__ == '__main__':
    pass
