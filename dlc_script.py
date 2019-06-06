import deeplabcut as dlc
import os

# Only works on windows rn


def new_vid(config, path):
    """Adds new video to project"""
    cfg = os.path.join(config, 'config.yaml')
    dlc.add_new_videos(cfg, [path])
    location = 'videos/' + path[path.last('/'):]
    dlc.analyze_videos(cfg, [os.path.join(config, location)])

if __name__ == '__main__':
    pass
