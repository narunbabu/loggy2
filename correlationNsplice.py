import numpy as np
import sys
from matplotlib import pyplot as plt
# sys.path.append('D:\SoftwareWebApps\Python\pyQt\LogSpliceUI\\')
from LateralCorr import mean_norm,get_delay
from flex import FlexXY,FlexLog
from Filters import *
from loggy_settings import well_folder, lwdVSwirelineFile, mnomonicsfile, params_file_path
# from collor_afftected_curve_v2 import *
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
    print(deptharr,drange,indxs )
    d,a=deptharr[indxs],dataarr[indxs]
    # print('d ',d)
    if len(d)>10:
        dt=d[1]-d[0]
        nan_indxs=np.isnan(a)
        return d[~nan_indxs],a[~nan_indxs],dt
    else:
        return np.array([]),np.array([]),np.nan
    
# drange=common_depth(log_bundle)


def get_rundepth_delays(flt_logs,run_indexs=[0,1],depthcol_name='DEPTH'):
    ma=[]
    rexpand_range=20
    lexpand_range=0
    flt_arrs=[]
    dt=0
    # for lb in log_bundle:
    #     flt_arrs.append(hist_filter(lb[logname].copy(),n_big_patches=1,hist_bins=100))
    darrays=np.array(flt_logs[depthcol_name])[run_indexs]
    drange=common_depth_of_runs(darrays)
    delay_max_corrs={}
    lognames=np.array(list(flt_logs.keys()))
    lognames=np.delete(lognames,np.where(lognames==depthcol_name))

    if np.isnan(drange[0]):
        for key in lognames:
            delay_max_corrs[key]=[0,0]
        return delay_max_corrs

    drange=np.array(drange)+np.array([-rexpand_range, lexpand_range])
    
    


    fg=plt.figure(figsize=(22.0,8))
    ax=[]
    

    quality_measure={} 
    for key in lognames: 
        # print(key) 
        # print(flt_logs[key])
        ma=[]   
        ora=[]
        or_d=[]
        quality_measure[key]=[]
        stds=[]
        new_d=[]
        log_specific_drange=drange.copy()
        print('******************************************')
        print('drange ',drange)
        # print(darrays)
        for da,fa in zip(darrays,np.array(flt_logs[key])[run_indexs]):
            # print('len da, fa ',len(da),len(fa))
            d,a,dt=getCurveWRange(da,fa,log_specific_drange)
            print(key, len(a))
            ora.append(a)
            or_d.append(d)
            
            if(len(a)>0):
                stds.append(np.std(a))
                if (stds[-1]>1):
                    log_specific_drange=[d[0],d[-1]]
                    ahist=np.histogram(a,31)
                    
                    # delay_weight= max(ahist[0])==max(ahist[0][13:17]),max(ahist[0])==max(ahist[0][0:4])
                    quality_measure[key].append([max(ahist[0])==max(ahist[0][13:17]),max(ahist[0])==max(ahist[0][0:4]),len(a),stds[-1]])
                    if len(new_d)<1:
                        new_d=np.arange(d[0],d[-1]+dt,dt)

                    logXY=np.column_stack((d,a))
                    flex_xy=FlexXY(logXY)
                    a=flex_xy.resampleY(new_d)
                    a=mean_norm(a)
                    
                    a[np.isnan(a)]=0   
            ma.append(a)
        
        
        if(len(a)>0) :
            if (sum(np.array(stds)<1)==0):  
            # stds=[quality_measure[key][0][-1],quality_measure[key][1][-1]]
                if len(stds)>1:
                    std_factor=abs(stds[0]-stds[1])/sum(stds)

                    print('std_factor: ',std_factor)  
                    if std_factor<0.7:
                        delay,corr=get_delay(ma[0],ma[1],dt,corrtype='+ve',dist2look=30)

                        vert_correlations_plot(fg,ax,len(lognames),ora,or_d,corr,delay,quality_measure[key])
                        # vert_correlations_plot(matwidget,ax,len(lognames),ora,or_d,corr,delay,quality_measure[key])

                        print('max(corr): ',max(corr[1]))
                    delay_max_corrs[key]=[delay,max(corr[1])]
        # print('quality_measure[key]: ',quality_measure[key])
    plt.show()
    return delay_max_corrs
def vert_correlations_plot(fg,ax,nlogs,ma,new_d,corr,delay,q_measure):
    plots_sofar=int(len(ax)/2)
    # ax.append(fg.getFigure().add_subplot(nlogs,1,plots_sofar+1))
    ax.append(fg.add_subplot(nlogs,1,plots_sofar+1) )
    l, b, w, h = ax[-1].get_position().bounds 
    qstr=''
    # for q in q_measure:
    #     qstr += 'Ratio: {0:3d},Ratio: {0:3d}, Nsamples: {1:4d} \n'.format(q[0],q[1],q[2])
    # print(q_measure)
    ax[-1].set_position([0.27,b,0.7,h])

    ax[-1].plot(new_d[0],ma[0],'b')
    ax[-1].plot(new_d[1],ma[1]-0.05,'g')
    ax[-1].plot(new_d[1]-delay,ma[1],'r')
    ax[-1].text(new_d[0][0]-10,0.02,str(plots_sofar+1))

    ax.append(fg.add_subplot(nlogs,2,plots_sofar+2) )
    # ax.append(fg.getFigure().add_subplot(nlogs,2,plots_sofar+2))
    ax[-1].set_position([0.03,b,0.21,h])
    ax[-1].plot(corr[0],corr[1],'b')
    ax[-1].text(delay,min(corr[1]),'Delay = %.2f'%delay)
    line = ax[-1].axvline(x=-delay, ymin=-1, ymax = +1, linewidth=1.5, color='c')
    # ax[-1].text(corr[0][0],0,str(q_measure))
def plot_logs(spliced_logs,lognames):
    fg=plt.figure(figsize=(22.0,8))
    ax=[]
    _,nlogs=spliced_logs.shape
    # plots_sofar=int(len(ax)
    for i in range(1,nlogs):
        ax.append(fg.add_subplot(nlogs-1,1,i) )
        l, b, w, h = ax[-1].get_position().bounds 
        ax[-1].set_position([0.05,b,0.92,h])
        ax[-1].plot(spliced_logs[:,0],spliced_logs[:,i],'b')
    plt.show()

def splice_w_delay(flt_logs,delays,logstep=0.1524,depthcol_name='DEPTH'):
    darrays=flt_logs[depthcol_name]
    # drange=common_depth_of_runs(darrays)
    for i,d in enumerate(delays):
        darrays[i]=darrays[i]-d
    lognames=np.array(list(flt_logs.keys()))
    lognames=np.delete(lognames,np.where(lognames==depthcol_name))
    
    flexlog = FlexLog(np.array([[0,0]]))
    for i in range(len(flt_logs[lognames[0]])):
        logXYY=darrays[i]
        for key in lognames:
            logXYY=np.column_stack((logXYY,flt_logs[key][i]))
        # flexlog=FlexLog(logXYY)
        flexlog.logExtend(logXYY,replace='bottom')
    return flexlog.getSplicedLog(logstep=logstep),lognames
def las_export(spliced_logs,lognames,file_w_path):
    import lasio
    params=np.load(params_file_path)
    las = lasio.LASFile()
    las.add_curve('DEPT', spliced_logs[:,0], unit='m')
    param_mnems=np.array([params[i]['mnemonic'] for i in range(len(params))])
    for i,lkey in enumerate(lognames):
        if lkey in param_mnems:
            indx=np.where(param_mnems==lkey)[0][0]
            print('*******************************')
            print(indx)
            las.add_curve(lkey, spliced_logs[:,i+1], unit=params[indx]['unit'])
        else:
            print('The log {} is not there in params, please add a unit to params, \n Until then this log will have unknown units'.format(lkey))
            las.add_curve(lkey, spliced_logs[:,i+1], unit='UNKWN')
    las.other = 'This las is generated by Laggy, the splicing module developed by Ameyem Geosolutions exclusively for Cairn Vedanta...'
    las.well['NULL'] = lasio.HeaderItem('NULL', value=-999.25, descr='NULL VALUE')
    las.well['WELL'] = lasio.HeaderItem('WELL', value='W1', descr='WELL')
    print('Writing to ',file_w_path)
    las.write(file_w_path)        

def find_delays_btwn_runs(flt_logs,depthcol_name='DEPTH'):
    delays_to_beapplied=[0]
    for i in range(1,len(flt_logs[depthcol_name])):
        
        delay_max_corrs=get_rundepth_delays(flt_logs,run_indexs=[i-1,i])
        delay_array=np.array([delay_max_corrs[key][0] for key in delay_max_corrs])
        maxcorrs=np.array([delay_max_corrs[key][1] for key in delay_max_corrs])
        indx_maxcorr=np.argmax(maxcorrs)
        delays_to_beapplied.append(delay_array[indx_maxcorr])
        # else:
        #     delays_to_beapplied.append(0)
        # mindelay=min(abs(delay_array))
        # meandelay=mean(abs(delay_array))<2*()
        # if (meandelay<2) | (mindelay<2):
        #     delay_to_beapplied=delay_array[np.argmin(abs(delay_array))]
        #     delays_to_beapplied.append(delay_to_beapplied)
        # else:
        #     delay_to_beapplied=delay_array[np.argmin(abs(delay_array))] # need to be modified when you get better idea what delay to be applied
        #     delays_to_beapplied.append(delay_to_beapplied)
    return delays_to_beapplied

if (__name__=='__main__'):

    log_bundle=np.load(well_folder+'..\proc_logs_bundle.npy')
    depthcol_name='DEPTH'
    print(log_bundle[0].keys())
    flt_logs=filtrt_logs(log_bundle,depthcol_name=depthcol_name,n_big_patches=1,hist_bins=600)
    
    delays_to_beapplied=find_delays_btwn_runs(flt_logs,depthcol_name=depthcol_name)
    print('******************************************')
    print('delays_to_beapplied :',delays_to_beapplied)
    # delays_to_beapplied=[-0.067]
    spliced_logs,lognames=splice_w_delay(flt_logs,delays_to_beapplied,depthcol_name=depthcol_name)
    np.save('spliced_logs.npy',(spliced_logs,lognames))    

    # plot_logs(spliced_logs,lognames)

    # spliced_logs,lognames=np.load('spliced_logs.npy')
    las_file_path='E:\Data\loggy_out_res.las'
    las_export(spliced_logs,lognames,las_file_path)
    print('Done!!!!!!!!!!!!!!!!!!!!')
    # def find_collor_effected(log_bundle):

    # print(delays_to_beapplied)


    # fg=plt.figure()
    # ax1=fg.add_subplot(211)

    # ax1.plot(new_d,ma[0],'b')

    # ax1.plot(new_d,ma[1]-0.1,'y')
    # ax1.plot(new_d-delay,ma[1],'r')
    # # ax1.plot(d+delay,a+25)
    # ax2=fg.add_subplot(212)
    # ax2.plot(corr[0],corr[1])
    # # print(corr[1])
    # plt.show()

