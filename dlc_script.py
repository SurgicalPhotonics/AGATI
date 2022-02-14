from deeplabcut import create_project, analyze_videos
import os


FILE_STRING = "DLC_resnet50_vocal_foldAug7shuffle1_1030000"  # for newer DLC
# FILE_STRING = 'DeepCut_resnet50_vocal_foldAug7shuffle1_1030000'
# Only works on windows rn


# might change how we handle pathing
def new_vid(config: str, path: str):
    """
    adds new video to deeplabcut project
    :param config: the name of the path to the config.yaml file
    :param path: the path of videos or directory containing
    :return:
    """
    cfg = os.path.join(config, "config.yaml")
    if not os.path.isdir(os.path.join(config, "videos")):
        os.mkdir(os.path.join(config, "videos"))
    create_project.add_new_videos(cfg, [path])
    location = os.path.join("videos", path[path.rfind("/") + 1 :])
    test = os.path.join(config, location)
    videotype = path[path.rfind(".") :]
    print("test? " + str(test))
    print("videotype " + videotype)
    analyze_videos(cfg, [test], videotype=videotype, TFGPUinference=False, save_as_csv=True)
    return os.path.join(config, location)


def analyze(config, path, h5_dir=os.getcwd() + "/output"):
    """Analyzes new video"""
    cfg = os.path.join(config, "config.yaml")
    name = analyze_videos(cfg, [path], videotype=path[path.rfind(".") :], destfolder=h5_dir, save_as_csv=True)
    h5 = h5_dir + "/" + name + ".h5"
    return h5, name


if __name__ == "__main__":
    pass
