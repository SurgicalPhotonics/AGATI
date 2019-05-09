import pandas as pd
import numpy as np

# might turn into class later
filename = 'file.h5' # will either pass in individually or read from list
data = np.array(pd.read_hdf(filename, 'df_with_missing'))
"""above line is incorrect right now but I can't see how the data is stored in 
the file until the network is done training so I'll fix it then"""
