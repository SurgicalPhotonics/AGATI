from deeplabcut import create_project
from deeplabcut import analyze_videos
import os


FILE_STRING = "DLC_resnet50_vocal_foldAug7shuffle1_1030000"  # for newer DLC
# FILE_STRING = 'DeepCut_resnet50_vocal_foldAug7shuffle1_1030000'
# Only works on windows rn


# might change how we handle pathing
def new_vid(config, path):
    """Adds new video to project"""
    print("path " + path)
    cfg = os.path.join(config, "config.yaml")
    print("config " + cfg)
    if not os.path.isdir(os.path.join(config, "videos")):
        os.mkdir(os.path.join(config, "videos"))
    create_project.add_new_videos(cfg, [path])
    location = os.path.join("videos", path[path.rfind("/") + 1 :])
    test = os.path.join(config, location)
    videotype = path[path.rfind(".") :]
    print("test? " + str(test))
    analyze_videos(cfg, [test], videotype=videotype)
    return os.path.join(config, location)


def analyze(config, path):
    """Analyzes new video"""
    cfg = os.path.join(config, "config.yaml")
    analyze_videos(cfg, [path], videotype=path[path.rfind(".") :])
    location = os.path.basename(os.path.normpath(path))
    new_vid = os.path.join(config, "videos", location)
    h5 = os.path.join(new_vid[0 : new_vid.rfind(".")], FILE_STRING + ".h5")
    return h5


if __name__ == "__main__":
    pass
