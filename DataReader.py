import pandas as pd
import numpy as np

con_const = 1
# Compares x-y coords of points to prev frame and eliminates large differences.

bps = ['AC1', 'AC2', 'LC1', 'LC2', 'LC3', 'LC4', 'LC5', 'LVP', 'RC1', 'RC2',
       'RC3', 'RC4', 'RC5', 'RVP']


def read_data(path):
    placeholder = pd.read_hdf(path)
    # fix next line to take all possible input -- exclude vocal and .h5
    data = placeholder['DeepCut_resnet50_vocalMay13shuffle1_1030000']
    sorted_data = []
    for part in bps:
        plist = []
        for i in range(len(data[part]['x'])):
            plist.append((data[part]['x'][i], data[part]['y'][i],
                          data[part]['likelihood'][i]))
        sorted_data.append(plist)
    clean_data(sorted_data)
    return sorted_data


def clean_data(data):
    """Removes outlier points caused by deeplabcut throwing points it can't find to random places.
    will need to return to this to fix issue when an important point like vocal process isn't visible for majority of
    the first 120 seconds."""
    for item in data:
        for i in range(len(item) - 1):
            if item[i][2] < con_const:
                item[i] = (0, 0, 0)


if __name__ == '__main__':
    data = read_data('vocal3DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5')
