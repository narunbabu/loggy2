print('Loading modules...')
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
from LasLoadThread import LasLoadThread
from helper import *
from flex import FlexLog
# from LogPlot import LogPlot
from LasTree import LasTree,treeWidgetFrmArray
from LateralCorr import lag_ix,get_delay,mean_norm
from Filters import *    

class VerticalCorr(QMainWindow):
    def __init__(self,parent=None):
        super(VerticalCorr, self).__init__(parent)
        from loggy_settings import well_folder, lwdVSwirelineFile, mnomonicsfile
        # projectFolder=r'D:\Ameyem Office\Projects\Cairn\W1\\'

        self.log_bundle=np.load(well_folder+'..\proc_logs_bundle.npy')
        self.flt_logs={}   
     
        for logname in self.log_bundle[0]['keys']:
            print(logname)
            self.flt_logs[logname]=[[] for i in range(len(self.log_bundle))]


            
        print('Starting main window...')


        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle('Vertical Correlations')
        self.setGeometry(100,100, 900,400)
        layout = QVBoxLayout(self.centralWidget)

        self.logscrollArea = QScrollArea(self)        
        layout.addWidget(self.logscrollArea)
        
        fw=QWidget()
        # fw.setMaximumWidth(120)
        # self.formLayout=QFormLayout()
        self.formLayout=QHBoxLayout()
        fw.setLayout(self.formLayout)
        layout.addWidget(fw)

        self.filtscrollArea = QScrollArea(self)        
        layout.addWidget(self.filtscrollArea)
        self.getFormLayerFilled()
        
        self.setCentralWidget(self.centralWidget)
      
        self.createDockWindows()
        
        self.run_mass_filter()

        
    def getFormLayerFilled(self):
        self.learray=[]
        # self.formLayout.addRow(QLabel(' '))
        # self.formLayout.addRow(QLabel('Calculated delays'))
        # self.formLayout.addRow(QLabel(' '))
        # for i,l in enumerate(self.delays.keys()):            
        #     self.learray.append( QLineEdit('%.2f'%self.delays[l])) #
        #     self.formLayout.addRow(QLabel(l),self.learray[-1])
        self.n_patches2retain_le=QLineEdit('1')
        self.n_hist_segments_le=QLineEdit('100')
        self.histFilter_btn = QPushButton("Remove Spikes")
        self.histForm=QFormLayout()
        
        self.histForm.addRow(QLabel('Retainpatches: '),self.n_patches2retain_le)
        self.histForm.addRow(QLabel('HistSegments: '), self.n_hist_segments_le)

        hfw=QWidget()
        hfw.setMaximumWidth(200)
        hfw.setLayout( self.histForm)
        # hfw.setMinimumWidth(120)
        
        self.formLayout.addWidget(hfw)
        self.formLayout.addWidget(self.histFilter_btn)
        self.histFilter_btn.clicked.connect(self.histFilter)
        # self.formLayout.addRow(QLabel('   '))

        # self.recal_btn = QPushButton("Recalculate")
        # self.formLayout.addRow(self.recal_btn)
        # self.recal_btn.clicked.connect(self.recalculateDelay)
    #     self.formLayout.addRow(QLabel(' '))
    #     self.save_btn = QPushButton("Save Curves")
    #     self.formLayout.addRow(self.save_btn)
    #     self.save_btn.clicked.connect(self.saveCorrCurves)

        
    # def applyDelayChange(self):
    #     for le,key in zip(self.learray,self.delays.keys()):
    #         self.delays[key]=np.float(le.text())            
    #         print(le.text())
    #     self.log_correlations_plot()
    # def recalculateDelay(self):
                
    #     self.logCorrelations()

    # def saveCorrCurves(self):
    #     print('Saving logs...')
    #     proc_logs={}
    #     for logname in self.delays.keys():
    #         if self.delays[logname] !=0:
    #             shift_depth=self.depth_col+self.delays[logname]
    #             shift_depth.shape=len(shift_depth),1
    #             # np.save('now.npy',(shift_depth,self.las[logname]))
    #             # print(shift_depth,self.las[logname])
    #             XY=np.append(shift_depth,self.las[logname].reshape(len(shift_depth),1),axis=1)
    #             XY.shape=len(shift_depth),2
    #             # print(XY)
    #             flexlog=FlexLog(XY)
    #             resamLog=flexlog.resampleY(self.depth_col)
    #         else:
    #             resamLog=self.las[logname]
    #         key=self.interestedKeynames[self.interestedLognames==logname][0]
    #         proc_logs[key]=resamLog            
    #     proc_logs['GR']=self.las[self.grlogname]
    #     proc_logs['DEPTH']=self.depth_col
    #     proc_logs['vlues_size']=np.size(self.las.values())
    #     proc_logs['keys']=self.interestedKeynames
    #     # proc_logs['test']='yes'
    #     bundle_file=self.wellFolder+'../proc_logs_bundle.npy'
    #     repeated=False
    #     if os.path.isfile(bundle_file):
    #         logbundle=np.load(bundle_file)
    #         for i,lb in enumerate(logbundle):
    #             if lb['vlues_size']==proc_logs['vlues_size']:
    #                 repeated=True
    #                 print('It is repeated so updated but not created...')
    #                 logbundle[i]=proc_logs
    #     else:
    #         logbundle=[]
    #     if not repeated:
    #         logbundle=np.append(logbundle,proc_logs)
    #     np.save(bundle_file,logbundle)
    #     print('Processed logs saved.. you can move on to next set...')
    #     time.sleep(2)
    #     self.close()
    def histFilter(self):
        depthcol_name='DEPTH'
        self.filtw = MatplotlibWidget(size=(22.0, 4), dpi=100  ) 
        self.filtscrollArea.setWidget(self.filtw)
        ax=self.filtw.getFigure().add_subplot(1,1,1)
        
                   
        hist_bins=np.int(self.n_hist_segments_le.text())
        n_big_patches=np.int(self.n_patches2retain_le.text())
        self.flt_logs[self.logname]=[]
        for i,lb in enumerate(self.log_bundle):
            self.flt_logs[self.logname][i]=hist_filter(lb[self.logname].copy(),n_big_patches=n_big_patches,hist_bins=hist_bins)
            ax.plot(lb[depthcol_name],self.flt_logs[self.logname][i])
        # print(flt_arrs)
    
    def run_mass_filter(self):
        hist_bins=np.int(self.n_hist_segments_le.text())
        n_big_patches=np.int(self.n_patches2retain_le.text())    
        
        for i,lb in enumerate(self.log_bundle):            
            for logname in lb['keys']:
                self.flt_logs[logname][i]=hist_filter(lb[logname].copy(),n_big_patches=n_big_patches,hist_bins=hist_bins)
            

    def logPlotPanel(self):
        print('Initiating plot widget...')
        self.logname=self.lastree.tree.selectedItems()[0].text(0)
        
        depthcol_name='DEPTH'
        # firstlog
        logdata=[]
        depthdata=[]
        self.mw = MatplotlibWidget(size=(22.0, 4), dpi=100  ) 
        self.logscrollArea.setWidget(self.mw)
        self.ax=self.mw.getFigure().add_subplot(1,1,1)

        self.filtw = MatplotlibWidget(size=(22.0, 4), dpi=100  ) 
        self.filtscrollArea.setWidget(self.filtw)
        ax2=self.filtw.getFigure().add_subplot(1,1,1)

        for i,lb in enumerate(self.log_bundle):
            # print(lb[self.logname],lb[depthcol_name]) 
            self.ax.plot(lb[depthcol_name],lb[self.logname])
            ax2.plot(lb[depthcol_name],self.flt_logs[self.logname][i])
        

            

            # logdata=np.append([logdata],[lb[logname]],axis=0  )     
            # depthdata=np.append([depthdata],[lb[depthcol_name] ],axis=0  ) 
        # print(logdata) 
        # self.depth_col=self.las[dcol]
        # dt=self.depth_col[1]-self.depth_col[0]
        # print('Spacing = ',dt)
        # gammacol=self.las[self.grlogname]
        # gammacol[np.isnan(gammacol)]=0
        # self.norm_gamma=mean_norm(gammacol)#[0:800]
         
        # l, b, w, h = self.ax.get_position().bounds 
        # self.ax.set_position([0.27,b+0.1,0.7,h])
        

        # self.lag_corrs={}
        # self.delays={}
        # self.normlogs={}
        # print('Calculating correlations...')
        # for logname in self.interestedLognames:
        #     if logname != self.grlogname:
        #         self.log_col=self.las[logname]  
        #         self.log_col[np.isnan(self.log_col)]=0            
        #         norm_blog=mean_norm(self.log_col)#[0:800]
        #         self.normlogs[logname]=norm_blog
        #         dist2look=100
        #         delay_estimation,lag_corr= get_delay(self.norm_gamma,norm_blog,dt,corrtype='abs',dist2look=dist2look)
        #         self.delays[logname]=-delay_estimation
        #         lagcor_range=np.arange(round(len(lag_corr[0])/2)-4*dist2look,round(len(lag_corr[0])/2)+4*dist2look)
        #         self.lag_corrs[logname]=(lag_corr[0][lagcor_range],lag_corr[1][lagcor_range])
        # self.log_correlations_plot()
        # self.getFormLayerFilled()
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

    def buildLogTree(self):
        self.lastree = LasTree()
        self.lastree.tree.headerItem().setText(0, "Categories")
        for lb in self.log_bundle:
            # logkeys=np.append(['GR'],lb['keys'])
            # print(logkeys)
            self.lastree.set_files(lb['keys'],make_tree_dict=False)
            mind,maxd=min(lb['DEPTH']),max(lb['DEPTH'])
            self.lastree.tree=treeWidgetFrmArray(self.lastree.tree,'({0:4.1f} to {1:4.1f})'.format(mind,maxd),lb['keys'])
        self.lastree.tree.itemSelectionChanged.connect(self.logPlotPanel)
        self.dock.setWidget(self.lastree.tree)
        print(dir(self.lastree.tree))
        print(help(self.lastree.tree.itemAt))
        print(self.lastree.tree.itemAt(1,0).text(0))
        

        
        
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
    mainWin = VerticalCorr()   

    mainWin.buildLogTree()
    # mainWin.logCorrelations()
    mainWin.show()
    sys.exit(app.exec_())