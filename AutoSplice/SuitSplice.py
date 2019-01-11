import lasio
import os
import numpy as np
from correlationNsplice import (common_depth_of_runs, getCurveWRange, get_delay,
get_indx_of_cont_patches,get_rundepth_delays,las_export)
from categorize_v2 import LogCategorize
from helper import *
from flex import FlexLogCurves
from loggy_settings import *
from LasTree import get_txtdict
from Filters import hist_filter
import matplotlib.pyplot as plt

class LateralLas():
    def __init__(self,suit,hist_bins=100,n_big_patches=1):
        self.hist_bins=hist_bins
        self.n_big_patches=n_big_patches
        self.curvetypesavoided = []
        self.depthcol_name='DEPTH'
        self.n_hist_segments=200
        self.type_dict=get_txtdict(mnomonicsfile,delimiter=' ')
        self.lc=LogCategorize(mnomonicsfile)
        for l in suit:
            print(l,'*******************************************')
            if os.path.isfile(suit[l]['path']):
                self.initiateLassing(suit[l]['path'])            
        
    def initiateLassing(self,path):
        self.las=lasio.read(path)
        self.lc.set_las(self.las)
        self.lc.lasCategorize()      
        self.interestedKeynames=self.lc.get_catePresent()
        self.interestedLognames=self.lc.getLogsPresent()
      
        self.makeXYY()
        self.applyfiltOnXYY(n_big_patches=self.n_big_patches,hist_bins=self.hist_bins)
        # if self.flexLogCurves:     
        # if 'self.flexLogCurves' in globals()   :
        if hasattr(self, 'flexLogCurves'):
            # print('in glooooooooooooooooooooooooobasl')
            self.flexLogCurves.sameSuitAppend(self.XYY,self.YcolNames)
        else:
            # print('noooooooooooooooooo in glooooooooooooooooooooooooobasl')
            self.flexLogCurves=FlexLogCurves(self.XYY,self.YcolNames)
        print('The path: ',path)
        # plt.plot(self.flexLogCurves.XY[:,0],self.flexLogCurves.XY[:,1:])
        # plt.show()
        self.curvetypesavoided=self.interestedKeynames.copy()
    def makeXYY(self):
        dcol=self.las.keys()[find_depth_indx(self.las)]
        self.XYY=self.las[dcol]
        self.YcolNames=[]
        for logname in self.interestedLognames:            
            log_cate=self.lc.get_category(logname,self.type_dict)
            # print(log_cate, self.curvetypesavoided)
            if log_cate not in self.curvetypesavoided:
                self.YcolNames.append(log_cate)           
                self.XYY=np.column_stack((self.XYY,self.las[logname]))    
        indxes=np.argsort(self.XYY[:,0])
        self.XYY=self.XYY[indxes,:]
        self.XYY=self.XYY[~np.isnan(self.XYY[:,0]),:]
        # print('self.XYY[:,0]... ',self.XYY[:,0])
        # plt.plot(self.XYY[:,0],self.XYY[:,1:])
        # plt.show()
    
    def applyfiltOnXYY(self,n_big_patches=1,hist_bins=100):
        # print()
        for j,log_cate in enumerate(self.YcolNames):
            print(log_cate)
            logdata=self.XYY[j+1,:]          
            if self.lc.isResistivityCurve(log_cate):                
                logdata[logdata==0]=0.001
                logdata=np.log10(logdata)
            
            res=hist_filter(logdata,n_big_patches=n_big_patches,hist_bins=hist_bins)
            if self.lc.isResistivityCurve(log_cate):
                res=np.power(10,res)
            # print('Summmation=  ',np.sum(logdata-self.XYY[j+1,:]))
            self.XYY[j+1,:]=res
   
class VerticalLas():
    def __init__(self,XY=np.array([[0,0]]),YKeys=[]):
        # self.lateralLas=lateralLas
        self.flexlog = FlexLogCurves(XY,YKeys)

    def extend(self,botlatlas,delaybottom=0):
        # darrays=flt_logs[depthcol_name]
        trows,tcols=self.flexlog.XY.shape
        if(trows<3):
            self.flexlog = FlexLogCurves(botlatlas.flexLogCurves.XY,botlatlas.flexLogCurves.YKeys)
            return
        brows,bcols=botlatlas.flexLogCurves.XY.shape
        botdarray=botlatlas.flexLogCurves.XY[:,0]-delaybottom
        toplogs=np.array(self.flexlog.YKeys)
        botlogs=np.array(botlatlas.flexLogCurves.YKeys)
        self.uniqueLogs=np.unique(np.append(toplogs,botlogs))
        topXY=np.zeros((trows,len(self.uniqueLogs)+1))+np.nan
        topXY[:,0]=self.flexlog.XY[:,0]
        botXY=np.zeros((brows,len(self.uniqueLogs)+1))+np.nan
        botXY[:,0]=botlatlas.flexLogCurves.XY[:,0]
        for i,ul in enumerate(self.uniqueLogs):
            idx=np.where(toplogs==ul)[0]
            if len(idx)==1:
                xy=self.flexlog.XY[:,idx[0]+1]
                xy.shape=trows
                # print('topXY[:,i+1].shape,xy.shape  ',topXY[:,i+1].shape,xy.shape)
                topXY[:,i+1]=xy
            idx=np.where(botlogs==ul)[0]
            # print(botlogs,ul)
            if len(idx)==1:
                # print(botlogs,ul)
                # print(i,' botlatlas.flexLogCurves.XY shape ',idx[0],botlatlas.flexLogCurves.XY.shape)
                xy=botlatlas.flexLogCurves.XY[:,idx[0]+1]
                xy.shape=brows
                botXY[:,i+1]=xy
        
        self.flexlog = FlexLogCurves(topXY,self.uniqueLogs)
        self.flexlog.logExtend(botXY,replace='bottom')
        return
    def doSplicing(self,sampling_inteval):
        self.sampling_int=sampling_inteval
        self.spliced_logs=self.flexlog.getSplicedLog(logstep=self.sampling_int)
        # return self.spliced_logs,self.uniqueLogs
    def export(self,las_file_path):       
        # self.status_label.setText('Exporting....') 
        las_export(self.spliced_logs,self.uniqueLogs,las_file_path)   
        print('Export success with {} sampling interval. File path is {}'.format(self.sampling_int,las_file_path))
    
class SuitSplice():
    def __init__(self,suits,hist_bins=100,n_big_patches=1):
        self.filepaths=[]
        self.resultLas=VerticalLas()
        self.suits=suits
        self.laterallases=[]
        self.hist_bins=hist_bins
        self.n_big_patches=n_big_patches
        
        for i in self.suits:
            # if i<2:
                self.laterallas=LateralLas(self.suits[i],hist_bins=self.hist_bins,n_big_patches=self.n_big_patches)
                self.laterallases.append(self.laterallas)
                self.resultLas.extend(self.laterallas,delaybottom=0)
                print('at suit ',i,' the shape is ',self.resultLas.flexlog.XY.shape)
                # plt.plot(self.laterallas.flexLogCurves.XY[:,0],self.laterallas.flexLogCurves.XY[:,1:])
                # plt.show()
                # self.laterallas.initiateLassing()
        # continue
        #     resultLas.append(LateralMerge(self.filepaths))
        # resultLas.splice(0.1524)
    def export(self,filepath,sampling_inteval):
               
        self.resultLas.doSplicing(sampling_inteval)
        self.resultLas.export(filepath)

if __name__=='__main__':
    suits=np.load('wellsuits.npy')[0]
    # print(suits)
    ss=SuitSplice(suits['W2'],hist_bins=400,n_big_patches=1)  #
    # np.save('ss.npy',[ss])

    print('saved ss.....................................')
    # ss.export('filepath.las',0.1524)
    plt.plot(ss.resultLas.flexlog.XY[:,0],ss.resultLas.flexlog.XY[:,1:])
    plt.show()
    # plt.plot(ss.laterallas.XYY[:,0],ss.laterallas.XYY[:,1:])
    # plt.show()
    # print(ss.laterallas.YcolNames)
    # np.save('suitsplice.npy',(ss,suits))
    # print('hello')
# from SuitSplice import *
# ss=np.load('ss.npy')[0]
# # ss.resultLas.flexlog.XY
# plt.plot(ss.laterallases[0].flexLogCurves.XY[:,0],ss.laterallases[0].flexLogCurves.XY[:,1:])
# # plt.plot(ss.laterallases[0].flexLogCurves.XY[:,0],ss.laterallases[0].flexLogCurves.XY[:,1:])
# plt.show()

# plt.plot(ss.resultLas.flexlog.XY[:,0],ss.resultLas.flexlog.XY[:,1:])
# plt.show()
