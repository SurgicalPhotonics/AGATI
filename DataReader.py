import pandas as pd
import numpy as np

# might turn into class later
bps = ['AC1', 'AC2', 'LC1', 'LC2', 'LC3', 'LC4', 'LC5', 'LVP', 'RC1', 'RC2',
       'RC3', 'RC4', 'RC5', 'RVP', 'LCART1', 'LCART2', 'RCART1', 'RCART2']


def read_data(path):
    placeholder = pd.read_hdf(path)
    data = placeholder['DeepCut_resnet50_vocal_strobeMay8shuffle1_200000']
    sorted_data = []
    for part in bps:
        plist = []
        for i in range(len(data[part]['x'])):
            plist.append((data[part]['x'][i], data[part]['y'][i]))
        sorted_data.append(plist)
    return sorted_data

if __name__ == '__main__':
    read_data('vocal0DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5')