from deeplabcut import create_project, analyze_videos
print("DeepLabCut functions Loaded")
import os
FILE_STRING = 'DLC_resnet50_vocal_foldAug7shuffle1_1030000' #for newer DLC
#FILE_STRING = 'DeepCut_resnet50_vocal_foldAug7shuffle1_1030000'
# Only works on windows rn


# might change how we handle pathing
def new_vid(config, path):
    """Adds new video to project"""
    cfg = os.path.join(config, 'config.yaml')
    # create_project.add_new_videos(cfg, [path])path
    # location = os.path.join('videos', path[path.rfind('/') + 1:])
    test = os.path.join(config, path)
    videotype = path[path.rfind('.'):]
    """stream = open(cfg, 'r')
    data = yaml.load(stream)
    data['video_sets'] += test
    with open(cfg, 'w') as file:
        file.write(yaml.dump(data, default_flow_style=False))"""
    analyze_videos(cfg, [test], videotype=videotype, destfolder=os.path.split(path)[0])
    return path


def analyze(config, path):
    """Analyzes new video"""
    cfg = os.path.join(config, 'config.yaml')
    analyze_videos(cfg, [path], videotype=path[path.rfind('.'):])
    location = os.path.basename(os.path.normpath(path))
    new_vid = os.path.join(config, "videos", location)
    h5 = os.path.join(new_vid[0: new_vid.rfind('.')], FILE_STRING + '.h5')
    return h5


"""def label(config, path):
    Creates labeled video from new video
    cfg = os.path.join(config, 'config.yaml')
    location = os.path.join('videos\\', path[path.rfind('/') + 1:])
    vpath = os.path.join(config, location)
    create_labeled_video(cfg, [vpath], videotype=path[path.rfind('.'):])
    new_vid = os.path.join(config, location[:location.rfind('.')])
    vid = new_vid + FILE_STRING + '_labeled' + path[path.rfind('.'):]
    return vid"""


if __name__ == '__main__':
    pass
