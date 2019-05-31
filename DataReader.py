import pandas as pd

con_const = 1  # How confident we want Deeplabcut to be of its point placement.

bps = ['AC1', 'AC2', 'LC1', 'LC2', 'LC3', 'LC4', 'LC5', 'LVP', 'RC1', 'RC2',
       'RC3', 'RC4', 'RC5', 'RVP']
# This will change (remove AC2) when we update training.


def read_data(path):
    """Reads Deeplabcut video data from dataframe using pandas."""
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
    """Removes points Deeplabcut has identified as outliers whose position it
    is not confident in from dataset."""
    for item in data:
        for i in range(len(item) - 1):
            if item[i][2] < con_const:
                item[i] = None


if __name__ == '__main__':
    data = read_data('vocalDeepCut_resnet50_vocalMay13shuffle1_1030000.h5')
