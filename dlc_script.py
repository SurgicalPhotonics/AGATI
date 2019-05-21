import deeplabcut as dlc
import os

# Only works on windows rn


def new_proj(path):
    """Creates new deeplabcut project"""
    project = input('Please input the name of the project (no spaces)')
    name = input('Enter your own name or that of the principal investigator '
                 '(no spaces)')
    dlc.create_new_project(project, name, 'r\'' + path)


def add_vid(cfg, path):
    """Adds video(s) to existing dlc project"""
    if os.path.isdir(path):
        input('Enter the filetype of the video you want analyzed. ex: \'.mp4\'')
        dlc.add_new_videos(cfg, '[r\'' + path + '\\' + ']')
    elif os.path.isfile(path):
        dlc.add_new_videos(cfg, 'r\'' + path)
    label_vids(cfg)


def label_vids(cfg):
    """Extracts frames and opens frame labelling GUI"""
    dlc.extract_frames(cfg)
    dlc.label_frames(cfg)
    dlc.create_training_dataset(cfg)
    dlc.check_labels(cfg)


def train(cfg):
    """Trains network."""
    dlc.train_network(cfg)
    dlc.evaluate_network(cfg)


def create_vids(cfg, path):
    """Labels chosen videos with dlc labels."""
    if os.path.isdir(path):
        dlc.analyze_videos(cfg, '[' + 'r\'' + path + '\\' + ']')
        dlc.create_labeled_video(cfg, '[' + 'r\'' + path + '\\' + ']')
    elif os.path.isfile(path):
        dlc.analyze_videos(cfg, 'r\'' + path)
        dlc.create_labeled_video(cfg, 'r\'' + path)


def refine(cfg):
    """Allows users to refine frames."""
    dlc.refine_labels(cfg)
    dlc.check_labels(cfg)
    dlc.merge_datasets(cfg)
    

if __name__ == '__main__':
    new_proj('vocal0DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5')