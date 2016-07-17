import os, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from financial_module.pickler import pickle_write, pickle_read
import datetime as dt
import calendar

plt.style.use('ggplot')

mklist = ['deeppink', 'darkviolet', 'slategrey', 'moccasin', 'olivedrab', 'goldenrod',
          'dodgerblue', 'coral', 'yellowgreen', 'skyblue', 'crimson']

# url = 'http://www.stoxx.com/download/historical_values/h_vstoxx.txt'
# vstoxx_index = pd.read_csv(url, index_col=0, header=2, parse_dates=True, dayfirst=True)
# pickle_write(vstoxx_index, 'vstoxx_index')
# vstoxx_index.plot(figsize=(10, 8))

# vstoxx_index = pickle_read('vstoxx_index')
# vstoxx_index = vstoxx_index[(vstoxx_index.index > '2013/12/31') & (vstoxx_index.index < '2014/4/1')]
# vstoxx_index.plot(figsize=(10, 8))

h5 = pd.HDFStore('vstoxx_march_2014.h5')
vstoxx_index = h5['vstoxx_index']
vstoxx_futures = h5['vstoxx_futures']
vstoxx_options = h5['vstoxx_options']
h5.close()

pricing_date = dt.datetime(2014, 3, 31)
maturity = dt.datetime(2014, 10, 17)
initial_value = vstoxx_index['V2TX'][pricing_date]
forward = vstoxx_futures[(vstoxx_futures.DATE == pricing_date) & (vstoxx_futures.MATURITY == maturity)].PRICE.values[0]
tol = 0.2
lower_strike = (1 - tol) * forward
upper_strike = (1 + tol) * forward
option_selection = vstoxx_options[
	(vstoxx_options.DATE == pricing_date)
	& (vstoxx_options.MATURITY == maturity)
	& (vstoxx_options.TYPE == 'C')
	& (vstoxx_options.STRIKE > lower_strike)
	& (vstoxx_options.STRIKE < upper_strike)]
