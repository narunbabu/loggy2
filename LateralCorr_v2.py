
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from LasTree import treeWidgetFrmDict,get_txtdict,write_txtdict
import numpy as np
from matplotlib.widgets import TextBox
# from PIL.ImageQt import ImageQt
# from scipy.misc.pilutil import toimage
import lasio
import os
import pyqtgraph as pg
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import time
# From files of app
import dockwidgets_rc
# from LasLoadThread import LasLoadThread
from helper import *
from flex import FlexLog
# from LogPlot import LogPlot
from LasTree import LasTree
from loggy_settings import *
def lag_ix(x,y,corrtype='+ve',dist2look=50):
        
    fullcorr = np.correlate(x,y,mode='full')
    halflen=round((fullcorr.size-1)/2)
    corr=fullcorr[halflen-dist2look:halflen+dist2look]
#     corr=fullcorr
    if corrtype=='+ve':
        pos_ix = np.argmax( corr) 
    elif corrtype=='-ve':
        pos_ix = np.argmin( corr)
    else:
        pos_ix = np.argmax( np.abs(corr) )
    lag_ix = pos_ix - (corr.size-1)/2
    return lag_ix
#     return halflen-dist2look+lag_ix
def get_delay(A,B,dt,corrtype='+ve',dist2look=50):
    timea=np.arange(0,len(A))
    timeb=np.arange(0,len(B))
    # compute cross correlation

    fullcorr = np.correlate(A, B, 'full')
    # maxlag = (fullcorr.size-1)/2 

    # lag = np.arange(-maxlag, maxlag+1)*dt

    samples2look=int(dist2look/dt)
    halflen=round((fullcorr.size-1)/2)

    corr=fullcorr[halflen-samples2look:halflen+samples2look]

    partlag = (corr.size-1)/2 

    lag = np.arange(-partlag, partlag+1)*dt
#     corr=fullcorr
    if corrtype=='+ve':
        pos_ix = np.argmax( corr) 
    elif corrtype=='-ve':
        pos_ix = np.argmin( corr)
    else:
        pos_ix = np.argmax( np.abs(corr) )
    lag_ix = pos_ix - (corr.size-1)/2

    delay_estimation = -(lag_ix-0.5)*dt
    # line = ax[1].axvline(x=-delay_estimation, ymin=np.min(coor), ymax = np.max(coor), linewidth=1.5, color='c')
    # print('delay: %.2f and delay in terms of n samples: %.2f'%(delay_estimation,delay_estimation/dt))
    return delay_estimation,(lag, corr)


def mean_norm(A):
    A=A-np.mean(A[~np.isnan(A)])
    return A/np.linalg.norm(A[~np.isnan(A)])
    # def cross_correlate(a,b):
            

class LateralCorr(QMainWindow):
    def __init__(self,parent=None):
        super(LateralCorr, self).__init__(parent)
        # self.wellFolder=well_folder
        print('Starting main window...')
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle('Lateral Correlations')
        self.setGeometry(100,100, 900,400)

        layout = QHBoxLayout(self.centralWidget)
        self.formLayout=QFormLayout()
        fw=QWidget()
        fw.setMaximumWidth(120)
        # fw.setMinimumHeight(400)
        fw.setLayout(self.formLayout)

        self.logscrollArea = QScrollArea(self)
        # self.corrscrollArea = QScrollArea(self)

        # layout.addWidget(self.corrscrollArea)
        layout.addWidget(fw)
        layout.addWidget(self.logscrollArea)
        self.setCentralWidget(self.centralWidget)

        # self.create_plotWindow()        
        self.createDockWindows()

        
    def getFormLayerFilled(self):
        self.learray=[]
        self.formLayout.addRow(QLabel(' '))
        self.formLayout.addRow(QLabel('Calculated delays'))
        self.formLayout.addRow(QLabel(' '))
        for i,l in enumerate(self.delays.keys()):            
            self.learray.append( QLineEdit('%.2f'%self.delays[l])) #
            self.formLayout.addRow(QLabel(l),self.learray[-1])
        self.delaysubmit_btn = QPushButton("Apply")
        self.formLayout.addRow(self.delaysubmit_btn)
        self.delaysubmit_btn.clicked.connect(self.applyDelayChange)
        self.formLayout.addRow(QLabel('   '))
        self.recal_btn = QPushButton("Recalculate")
        self.formLayout.addRow(self.recal_btn)
        self.recal_btn.clicked.connect(self.recalculateDelay)
        self.formLayout.addRow(QLabel(' '))
        self.save_btn = QPushButton("Save Curves")
        self.formLayout.addRow(self.save_btn)
        self.save_btn.clicked.connect(self.saveCorrCurves)

        
    def applyDelayChange(self):
        for le,key in zip(self.learray,self.delays.keys()):
            self.delays[key]=np.float(le.text())            
            print(le.text())
        self.log_correlations_plot()
    def recalculateDelay(self):
                
        self.logCorrelations()

    def saveCorrCurves(self):
        print('Saving logs...')
        proc_logs={}
        for logname in self.delays.keys():
            if self.delays[logname] !=0:
                shift_depth=self.depth_col+self.delays[logname]
                shift_depth.shape=len(shift_depth),1
                # np.save('now.npy',(shift_depth,self.las[logname]))
                # print(shift_depth,self.las[logname])
                XY=np.append(shift_depth,self.las[logname].reshape(len(shift_depth),1),axis=1)
                XY.shape=len(shift_depth),2
                # print(XY)
                flexlog=FlexLog(XY)
                resamLog=flexlog.resampleY(self.depth_col)
            else:
                resamLog=self.las[logname]
            key=self.interestedKeynames[self.interestedLognames==logname][0]
            proc_logs[key]=resamLog            
        proc_logs['GR']=self.las[self.grlogname]
        proc_logs['DEPTH']=self.depth_col
        proc_logs['vlues_size']=np.size(self.las.values())
        proc_logs['keys']=self.interestedKeynames
        # proc_logs['test']='yes'
        bundle_file=proc_logs_bundle_file
        repeated=False
        if os.path.isfile(bundle_file):
            logbundle=np.load(bundle_file)
            print('______________________^^^^__________________________')
            print(len(logbundle))
            for i,lb in enumerate(logbundle):
                if lb['vlues_size']==proc_logs['vlues_size']:
                    repeated=True
                    print('________________________________________________')
                    print('It is repeated so updated but not created...')
                    logbundle[i]=proc_logs
                    break
                # else:
                #     print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')
                #     print('It is not repeated so  created...')
                
        else:
            logbundle=[]
        if not repeated:
            if (len(logbundle)>0):
                if proc_logs['DEPTH'][0]>logbundle[-1]['DEPTH'][0]:
                    logbundle=np.append(logbundle,proc_logs)
                else:
                    logbundle=np.append(proc_logs,logbundle)
            else:
                logbundle=np.append(proc_logs,logbundle)
                
        np.save(bundle_file,logbundle)
        print('Processed logs saved.. you can move on to next set...')
        time.sleep(2)
        self.close()
        
            

    def logCorrelations(self):
        print('Initiating plot widget...')
        self.interestedLognames=np.array([self.treeview_dict['Log'][key][0] for key in self.treeview_dict['Log']])

        # self.interestedLognames=np.array(self.interestedLognames)
        # print('self.interestedLognames : ',self.interestedLognames)
        self.interestedKeynames=np.array([k for k in self.treeview_dict['Log'].keys()])
        self.grlogname=self.treeview_dict['Log']['GR'][0]          
        
        dcol=self.las.keys()[find_depth_indx(self.las)]
        self.depth_col=self.las[dcol]
        dt=self.depth_col[1]-self.depth_col[0]
        print('Spacing = ',dt)
        gammacol=self.las[self.grlogname]
        gammacol[np.isnan(gammacol)]=0
        self.norm_gamma=mean_norm(gammacol)#[0:800]

        self.lag_corrs={}
        self.delays={}
        self.normlogs={}
        print('Calculating correlations...')
        for logname in self.interestedLognames:
            if logname != self.grlogname:
                self.log_col=self.las[logname]  
                self.log_col[np.isnan(self.log_col)]=0            
                norm_blog=mean_norm(self.log_col)#[0:800]
                self.normlogs[logname]=norm_blog
                dist2look=100
                delay_estimation,lag_corr= get_delay(self.norm_gamma,norm_blog,dt,corrtype='abs',dist2look=dist2look)
                self.delays[logname]=-delay_estimation
                lagcor_range=np.arange(round(len(lag_corr[0])/2)-4*dist2look,round(len(lag_corr[0])/2)+4*dist2look)
                self.lag_corrs[logname]=(lag_corr[0][lagcor_range],lag_corr[1][lagcor_range])
        self.log_correlations_plot()
        self.getFormLayerFilled()
    def log_correlations_plot(self):
        self.mw = MatplotlibWidget(size=(22.0, len(self.interestedLognames)*1.6), dpi=100)   
        self.logscrollArea.setWidget(self.mw)
        print('Plotting...')
        self.ax=[]
        for i,logname in enumerate(self.normlogs.keys()):
            self.ax.append(self.mw.getFigure().add_subplot(len(self.normlogs),1,i+1) )
            l, b, w, h = self.ax[-1].get_position().bounds 
            self.ax[-1].set_position([0.27,b+0.1,0.7,h])
            # self.log_col=self.las[logname]  
            # self.log_col[np.isnan(self.log_col)]=0            
            # norm_blog=mean_norm(self.log_col)#[0:800]
            depthb_shift=self.depth_col+self.delays[logname]
            self.ax[-1].plot(self.depth_col,self.normlogs[logname],'b')
            self.ax[-1].plot(self.depth_col,self.norm_gamma,'r')
            self.ax[-1].plot(depthb_shift,self.normlogs[logname],'magenta')
            self.ax[-1].text(self.depth_col[0]-50,0.02,logname)

        lenax=len(self.ax)
        for i,logname in enumerate(self.lag_corrs.keys()):
            self.ax.append(self.mw.getFigure().add_subplot(len(self.normlogs),2,lenax+i+1) )
            l, b, w, h = self.ax[i].get_position().bounds
            self.ax[-1].set_position([0.03,b,0.21,h])
            self.ax[-1].plot(self.lag_corrs[logname][0],self.lag_corrs[logname][1],'b')
            self.ax[-1].text(self.delays[logname],min(self.lag_corrs[logname][1]),'Delay = %.2f'%self.delays[logname])
            line = self.ax[-1].axvline(x=self.delays[logname], ymin=-1, ymax = +1, linewidth=1.5, color='c')
            self.ax[-1].text(self.lag_corrs[logname][0][0],0.4,logname)
                
        self.mw.draw()
        print('Complete...')

    def buildLogTree(self,lases):
        w = LasTree()
        # self.lasLoadThread = LasLoadThread(files=files_w_path)

        self.lases=lases
        if (len(self.lases)>0):
            if (len(self.lases[0].keys())>0):
                self.las=self.lases[0]      
                w.set_files(self.las.keys())
                del w.treeview_dict['Log']['NA']
                self.treeview_dict=w.treeview_dict
                
                w.buildTreeWidget()          

        self.dock.setWidget(w.tree)         
        
    def createDockWindows(self):        
        self.dock = QDockWidget("Log Files", self)
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # dock.setWidget(self.lastree.tree)        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        
        # self.set_category_button = QPushButton('Set Category', self)
        # dock = QDockWidget("Set", self)
        # dock.setWidget(self.set_category_button)
        # self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        # self.set_category_button.clicked.connect(self.set_category)

        # dock = QDockWidget("Logs", self)        
        # dock.setWidget(self.logtree.tree)
        # self.addDockWidget(Qt.LeftDockWidgetArea, dock)
    
if __name__ == '__main__':
    
    import sys

    app = QApplication(sys.argv)
    
    # wellFolder=r'D:\Ameyem Office\Projects\Cairn\W1\LAS\\'
    
    # from loggy_settings import well_folder, lwdVSwirelineFile, mnomonicsfile
    

    files=np.array(os.listdir(well_folder)[:])
    

    files_w_path=[well_folder+'W1_SUITE2_COMPOSITE.las']
    files_w_path=[well_folder+files[0]]
    lases=[lasio.read(files_w_path[0])]

    mainWin = LateralCorr()
    mainWin.buildLogTree(lases)
    mainWin.logCorrelations()
    mainWin.show()
    sys.exit(app.exec_())