from pandas import read_hdf

con_const = .99  # How confident we want Deeplabcut to be of its point placement.

#Each point marked in DeepLabCut

bps = ['AC', 'LC1', 'LC2', 'LC3', 'LC4', 'LC5', 'LVP', 'RC1', 'RC2',
       'RC3', 'RC4', 'RC5', 'RVP']


def read_data(path):
    """Reads Deeplabcut video data from dataframe using pandas."""
    placeholder = read_hdf(path)
    # fix next line to take all possible input -- exclude vocal and .h5
    #data = placeholder['DLC_resnet50_vocal_foldAug7shuffle1_1030000'] #Newer DLC
    data = placeholder['DeepCut_resnet50_vocal_foldAug7shuffle1_1030000']
    sorted_data = []
    for part in bps:
        plist = []
        for i in range(len(data[part]['x'])):
            if data[part]['likelihood'][i] >= con_const:
                plist.append((data[part]['x'][i], data[part]['y'][i],
                              data[part]['likelihood'][i]))
            else:
                plist.append(None)
        sorted_data.append(plist)
    return sorted_data


if __name__ == '__main__':
    data = read_data('vocalDeepCut_resnet50_vocalMay13shuffle1_1030000.h5')
