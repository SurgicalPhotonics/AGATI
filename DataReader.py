import pandas as pd
import numpy as np

window_x = 100
window_y = 100
# Compares x-y coords of points to prev frame and eliminates large differences.

bps = ['AC1', 'AC2', 'LC1', 'LC2', 'LC3', 'LC4', 'LC5', 'LVP', 'RC1', 'RC2', 'RC3', 'RC4', 'RC5', 'RVP', 'LCART1',
       'LCART2', 'RCART1', 'RCART2']


def read_data(path):
    placeholder = pd.read_hdf(path)
    data = placeholder['DeepCut_resnet50_vocal_strobeMay8shuffle1_200000']
    sorted_data = []
    for part in bps:
        plist = []
        for i in range(len(data[part]['x'])):
            plist.append((data[part]['x'][i], data[part]['y'][i]))
        sorted_data.append(plist)
    clean_data(sorted_data)
    return sorted_data


def clean_data(data):
    """Removes outlier points caused by deeplabcut throwing points it can't find to random places.
    will need to return to this to fix issue when an important point like vocal process isn't visible for majority of
    the first 120 seconds."""
    for item in data:
        sumx = 0
        sumy = 0
        for i in range(120):
            sumx += item[i][0]
            sumy += item[i][1]
        meanx = sumx / 120
        meany = sumy / 120
        i = 0
        start = -1
        while i < len(item) and start == -1:
            if meanx - 50 < item[i][0] < meanx + 50 and meany - 50 < item[i][1] < meany + 50:
                start = i
            i += 1
        for j in range(start):
            item[j] = (0.0, 0.0)
        last = item[start]
        for j in range(start, len(item)):
            if last[0] - window_x > item[j][0] or last[0] + window_x < item[j][0] or last[1] - window_y > item[j][1] or\
                    last[1] + window_y < item[j][1]:
                item[j] = (0.0, 0.0)
            else:
                last = item[j]


if __name__ == '__main__':
    data = read_data('vocal1DeepCut_resnet50_vocal_strobeMay8shuffle1_200000.h5')
