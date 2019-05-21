# VCTrack
Analyzer for data collected on vocal cord movement using DeepLabCut. 

Current version: Extremely disorganized. Haven't decided on overall structure yet

Current version only works for windows. Basic function will automatically edit deeplabcut config.yaml file, but more advanced changes will require user to directly edit config file. This will not interfere with program, and is encouraged. We recommend notepad++ to edit config file. If the user moves the dlc file directory within their file system, they must edit the displayed paths in the config file.

Midline code is still there in case reviewers want to see that expanded on. No current plans to continue that path, though. 

End Goal: Create a gui that allows doctors and researchers to input video. Program will pass everything through deeplabcut, analyze the dataset and return a labeled video that outputs full analysis of the cords. 

Surgical Photonics and Engineering Laboratory. 
Massachusetts Eye and Ear Infirmary
