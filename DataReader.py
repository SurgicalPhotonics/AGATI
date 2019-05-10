import pandas as pd
import numpy as np

# might turn into class later
filename = 'vocal0DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5'
placeholder = pd.read_hdf(filename)
data = placeholder['DeepCut_resnet50_vocal_strobeMay8shuffle1_200000']

