import pandas as pd
import numpy as np

filename = 'vocal0DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5'

# might turn into class later
if __name__ == "__main__":
    placeholder = pd.read_hdf(filename)
    data = placeholder['DeepCut_resnet50_vocal_strobeMay8shuffle1_200000']
    sorted_data = []
    bps = ['AC1', 'AC2', 'LC1', 'LC2', 'LC3', 'LC4', 'LC5', 'LVP', 'RC1', 'RC2',
           'RC3', 'RC4', 'RC5', 'RVP', 'LCART1', 'LCART2', 'RCART1', 'RCART2']
    for part in bps:
        plist = []
        for i in range(len(data[part]['x'])):
            plist.append([data[part]['x'][i], data[part]['y'][i]])
        sorted_data.append(plist)
    print('something')

