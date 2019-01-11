import numpy as np
import sys
from matplotlib import pyplot as plt
sys.path.append('D:\SoftwareWebApps\Python\pyQt\LogSpliceUI\\')
from LateralCorr import mean_norm,get_delay
from flex import FlexXY
from Filters import *
projectFolder=r'D:\Ameyem Office\Projects\Cairn\W1\\'
log_bundle=np.load(projectFolder+'proc_logs_bundle.npy')

logname='GR';depthcol_name='DEPTH'
# logXY=np.append(log_bundle[0][depthcol_name].T,order_filter(log_bundle[0][logname].copy(),n_big_patches=1,hist_patches=100).T,axis=1)
logXY=np.column_stack((log_bundle[0][depthcol_name],hist_filter(log_bundle[0][logname].copy(),n_big_patches=1,hist_bins=100)))


plt.hist(logXY[:,1],50)
flex_xy=FlexXY(logXY[~np.isnan(logXY[:,1]),:])
y=flex_xy.resampleY(logXY[:,0])


# from random import randrange
# from pandas import Series

# from statsmodels.tsa.seasonal import seasonal_decompose


# # series = [i+randrange(10) for i in range(1,100)]
# # np.array(series)


# series=y[~np.isnan(y)]
# fig2=plt.figure()
# result = seasonal_decompose(series, model='multiplicative', freq=500) # multiplicative, additive


# # result.plot()
# # plt.show()
# # fig=plt.figure()
# plt.hist(result.trend,1000)

# # print(dir(result))
plt.show()
