import numpy as np
import sys
from matplotlib import pyplot as plt
# sys.path.append('D:\SoftwareWebApps\Python\pyQt\LogSpliceUI\\')
from LateralCorr import mean_norm,get_delay
from flex import FlexXY
from Filters import *
from loggy_settings import well_folder, lwdVSwirelineFile, mnomonicsfile

def common_depth_of_runs(depth_arrays):
    if len(depth_arrays)>2:
        print('Please input two depth arrays...')
        return
    dranges=[]
    dointersect=False
    for da in depth_arrays:
        dranges.append([da.min(),da.max()])
    for mx in max(dranges):
        for mn in min(dranges):
            if not dointersect:
                dointersect=mx<mn   
    if dointersect:
        return [min(max(dranges)),max(min(dranges))]
    else:
        return [np.nan, np.nan]
# def common_depth_logexists(log_bundle):  
#     depth_range=common_depth(log_bundle)
#     d,a=getCurveWRange(lb[depthcol_name],fa,drange)

def getCurveWRange(deptharr,dataarr,drange):
    indxs= (deptharr>=drange[0]) & (deptharr<=drange[1])
    
    d,a=deptharr[indxs],dataarr[indxs]
    print(np.unique(np.diff(d)))
    dt=d[1]-d[0]
    nan_indxs=np.isnan(a)
    return d[~nan_indxs],a[~nan_indxs],dt
    
# drange=common_depth(log_bundle)


def get_rundepth_delay(flt_logs,run_indexs=[0,1],depthcol_name='DEPTH'):
    ma=[]
    expand_range=50
    flt_arrs=[]
    dt=0
    # for lb in log_bundle:
    #     flt_arrs.append(hist_filter(lb[logname].copy(),n_big_patches=1,hist_bins=100))
    drange=common_depth_of_runs(flt_logs[depthcol_name][run_indexs])
    drange=np.array(drange)+np.array([-expand_range, expand_range])
    delays={}
    for key in flt_logs.keys():        
        for da,fa in zip(flt_logs[depthcol_name],flt_logs[key])
            d,a,dt=getCurveWRange(dc,fa,drange)
            if len(ma)==0:
                new_d=np.arange(d[0],d[-1]+dt,dt)
            logXY=np.column_stack((d,a))
            flex_xy=FlexXY(logXY)
            a=flex_xy.resampleY(new_d)
            a=mean_norm(a)
            a[np.isnan(a)]=0   
            ma.append(a)
        delay,corr=get_delay(ma[0],ma[1],dt,corrtype='+ve',dist2look=30)
        delays[key]=delay
    return delays



if (__name__=='__main__'):

    log_bundle=np.load(well_folder+'..\proc_logs_bundle.npy')
    print(log_bundle[0].keys())
    flt_logs={}
    dt=0
    depthcol_name='DEPTH'
    flt_logs[depthcol_name] =[lb[depthcol_name] for lb in log_bundle]
    for logname in log_bundle[0]['keys']:
            print(logname)
            flt_logs[logname]=[[] for i in range(len(log_bundle))]
    
    for i,lb in enumerate(log_bundle):            
            for logname in lb['keys']:
                flt_logs[logname][i]=hist_filter(lb[logname].copy(),n_big_patches=1,hist_bins=100)

    new_d,ma,delay,corr=get_rundepth_delay(flt_logs,logname='GR')

    # def find_collor_effected(log_bundle):

    print(delay)


    fg=plt.figure()
    ax1=fg.add_subplot(211)

    ax1.plot(new_d,ma[0],'b')

    ax1.plot(new_d,ma[1]-0.1,'y')
    ax1.plot(new_d-delay,ma[1],'r')
    # ax1.plot(d+delay,a+25)
    ax2=fg.add_subplot(212)
    ax2.plot(corr[0],corr[1])
    # print(corr[1])
    plt.show()

