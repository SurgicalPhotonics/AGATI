import pandas as pd
# might turn into class later
filename = 'file.h5' # will either pass in individually or read from list
data = pd.read_hdf(filename, 'df_with_missing')
