print("Create Project")
from deeplabcut import create_project

print("Analyze videos")
from deeplabcut import analyze_videos

print("DeepLabCut functions Loaded")
print("OSPath")
from os import path as ospath


FILE_STRING = "DLC_resnet50_vocal_foldAug7shuffle1_1030000"  # for newer DLC
# FILE_STRING = 'DeepCut_resnet50_vocal_foldAug7shuffle1_1030000'
# Only works on windows rn


# might change how we handle pathing
def new_vid(config, path):
    """Adds new video to project"""
    cfg = ospath.join(config, "config.yaml")
    create_project.add_new_videos(cfg, [path])
    location = ospath.join("videos", path[path.rfind("/") + 1 :])
    test = ospath.join(config, location)
    videotype = path[path.rfind(".") :]
    """stream = open(cfg, 'r')
    data = yaml.load(stream)
    data['video_sets'] += test
    with open(cfg, 'w') as file:
        file.write(yaml.dump(data, default_flow_style=False))"""
    analyze_videos(cfg, [test], videotype=videotype)
    return ospath.join(config, location)


def analyze(config, path):
    """Analyzes new video"""
    cfg = ospath.join(config, "config.yaml")
    analyze_videos(cfg, [path], videotype=path[path.rfind(".") :])
    location = ospath.basename(ospath.normpath(path))
    new_vid = ospath.join(config, "videos", location)
    h5 = ospath.join(new_vid[0 : new_vid.rfind(".")], FILE_STRING + ".h5")
    return h5


"""def label(config, path):
    Creates labeled video from new video
    cfg = ospath.join(config, 'config.yaml')
    location = ospath.join('videos\\', path[path.rfind('/') + 1:])
    vpath = ospath.join(config, location)
    create_labeled_video(cfg, [vpath], videotype=path[path.rfind('.'):])
    new_vid = ospath.join(config, location[:location.rfind('.')])
    vid = new_vid + FILE_STRING + '_labeled' + path[path.rfind('.'):]
    return vid"""


if __name__ == "__main__":
    pass
