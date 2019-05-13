import deeplabcut as dlc

def run_dlc(path):
    project = input('Please input the name of the project (no spaces)')
    name = input('Enter your own name or that of the principal investigator (no spaces)')
    dlc.create_new_project(project, name, path)
    dlc.extract_frames(path)
    dlc.label_frames(path)
    # Find way to change label options in config
    dlc.check_labels(path)



if __name__ == '__main__':
    run_dlc('vocal0DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5')
