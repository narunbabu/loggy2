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
# from LasLoadThread import LasLoadThread
from helper import *
from flex import FlexLog
# from LogPlot import LogPlot
from LasTree import LasTree,treeWidgetFrmArray,get_txtdict
from LateralCorr import lag_ix,get_delay,mean_norm
from Filters import *    
from correlationNsplice import *
from loggy_settings import *
class MyScrollArea(QScrollArea):
    def __init__(self,parent=None):
        super(MyScrollArea, self).__init__(parent)
        self.setMinimumHeight(250)

class VerticalCorrNSplice(QMainWindow):
    def __init__(self,parent=None):
        super(VerticalCorrNSplice, self).__init__(parent)
        
        self.depthcol_name='DEPTH'
        self.display_splice=False
        self.type_dict=get_txtdict(mnomonicsfile,delimiter=' ')
        self.get_logbundle()
        self.delays_to_beapplied=[0]*len(self.log_bundle)
        print('Starting main window...')

        #Container Widget        
        widget = QWidget()
        main_layout = QVBoxLayout(self)

        self.logscrollArea = MyScrollArea(self)        
        main_layout.addWidget(self.logscrollArea) #1st widget
        # self.logscrollArea.setMinimumHeight(250)

        fw=QWidget()        
        fw.setMaximumWidth(400)       

        # self.formLayout=QFormLayout()
        self.getHistFormLayerFilled()
        

        fw.setLayout(self.histForm)        
        main_layout.addWidget(fw)       #2nd widget


        
        self.filtscrollArea = MyScrollArea(self)    
        main_layout.addWidget(self.filtscrollArea) #3rd widget

        
        corr_fw=QWidget()      
        self.corrformLayout=QFormLayout()        
        corr_fw.setLayout(self.corrformLayout)
        # This is filled in dlay_form function
        self.fill_delayForm()        
        main_layout.addWidget(corr_fw)   #4th widget

        self.delay_apply_btn = QPushButton("Apply delay")
        self.delay_apply_btn.clicked.connect(self.plotafterdelayapplied)
        main_layout.addWidget(self.delay_apply_btn)   #5th widget
        

        self.verticalDelayCorrScroll = MyScrollArea(self)        
        main_layout.addWidget(self.verticalDelayCorrScroll)   #6th widget
        

        splice_w=QWidget()
        self.sampling_inteval=QLineEdit('0.1524')        
        self.spliceForm=QHBoxLayout()        
        self.spliceForm.addWidget(QLabel('Sampling Interval: '))
        self.spliceForm.addWidget(self.sampling_inteval)
        self.spliceForm.addWidget(QLabel('m'))     
        self.splice_btn = QPushButton("Splice")
        self.splice_btn.clicked.connect(self.splice_logs)  
        
        self.spliceForm.addWidget(self.splice_btn  )
        
        splice_w.setLayout(self.spliceForm)
        main_layout.addWidget(splice_w)  #7th widget

        

        self.splicedisplayscroll = MyScrollArea(self)        
        main_layout.addWidget(self.splicedisplayscroll)   #8th widget



        self.export_btn = QPushButton("Export las")
        self.export_btn.clicked.connect(self.export)
        main_layout.addWidget(self.export_btn)   #9th widget
        self.status_label=QLabel('')
        self.status_label.setText('Epxport status none')
        main_layout.addWidget(self.status_label)   #9th widget
        
        widget.setLayout(main_layout)
        
       

        central_scroll=QScrollArea(self) 
        central_scroll.setWidget(widget)
        central_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        layout = QVBoxLayout(self)
        layout.addWidget(central_scroll)
        central_scroll.setWidgetResizable(True)
        self.centralWidget =  QWidget() 
        self.setWindowTitle('Vertical Correlations')
        self.setGeometry(100,100, 900,400)              
        # widget.setGeometry(100,100, 900,400)
        self.centralWidget.setLayout(layout)
        self.setCentralWidget(self.centralWidget)
      
        self.createDockWindows()
        
        self.run_mass_filter()
        self.logPlotPanel()

        # self.verticalDelayCorrPanel()
    def get_logbundle(self):
        
        # projectFolder=r'D:\Ameyem Office\Projects\Cairn\W1\\'

        self.log_bundle=np.load(well_folder+'..\proc_logs_bundle.npy')
        self.flt_logs={}   
        
        lognames=list(self.log_bundle[0]['keys'])
        lognames.append(self.depthcol_name)
        for logname in self.log_bundle[0]['keys']:
            # print(logname)
            self.flt_logs[logname]=[[] for i in range(len(self.log_bundle))]

        
    def getHistFormLayerFilled(self):
        self.n_patches2retain_le=QLineEdit('1')
        self.n_hist_segments_le=QLineEdit('100')
        self.histFilter_btn = QPushButton("Remove Spikes")

        self.histForm=QHBoxLayout()
        
        self.histForm.addWidget(QLabel('Retain Patches: '))
        self.histForm.addWidget(self.n_patches2retain_le)
        self.histForm.addWidget(QLabel('Hist Segments: '),)
        self.histForm.addWidget(self.n_hist_segments_le)
        self.histForm.addWidget(self.histFilter_btn)

        self.histFilter_btn.clicked.connect(self.histFilter)

    def getCorrFormLayerFilled(self):
        pass
        # self.learray=[]
        # self.formLayout.addRow(QLabel(' '))
        # self.formLayout.addRow(QLabel('Calculated delays'))
        # self.formLayout.addRow(QLabel(' '))
        # for i,l in enumerate(self.delays.keys()):            
        #     self.learray.append( QLineEdit('%.2f'%self.delays[l])) #
        #     self.formLayout.addRow(QLabel(l),self.learray[-1])
        # self.n_patches2retain_le=QLineEdit('1')
        # self.n_hist_segments_le=QLineEdit('100')
    def fill_delayForm(self):
        self.docorr_btns=[]
        self.corr_le=[]
        for i in  range(1,len(self.log_bundle)):
            self.docorr_btns.append( QPushButton("Calculate vertical Delay: Runs "+str(i)+' to '+str(i+1)))
            self.corr_le.append(QLineEdit('0.0'))
            self.corrformLayout.addRow(self.docorr_btns[i-1])
            self.corrformLayout.addRow(QLabel('Calculated delay:'),self.corr_le[i-1])
            # self.docorr_btns[i-1].clicked.connect(self.doVCorrelation)
            self.docorr_btns[i-1].clicked.connect(lambda state, x=i-1:self.verticalDelayCorrPanel(x))
    def verticalDelayCorrPanel(self,startrun):      
        print('startrun ',startrun)
        self.run_mass_filter()
        # get_rundepth_delays(self.vertdelay_w,flt_logs,run_indexs=[0,1],depthcol_name='DEPTH')
        # ax=self.vertdelay_w.getFigure().add_subplot(1,1,1)
        delay_max_corrs=get_rundepth_delays(self.flt_logs,run_indexs=[startrun,startrun+1],depthcol_name='DEPTH')
        print('delay_max_corrs',delay_max_corrs)
        delay_array=np.array([delay_max_corrs[key][0] for key in delay_max_corrs])
        print('delay_array',delay_array)
        maxcorrs=np.array([delay_max_corrs[key][1] for key in delay_max_corrs])
        if len(maxcorrs)>1:
            indx_maxcorr=np.argmax(maxcorrs)
            self.delays_to_beapplied[startrun+1]=delay_array[indx_maxcorr]
        else:
            self.delays_to_beapplied[startrun+1]=0
        self.corr_le[startrun].setText(str(self.delays_to_beapplied[startrun+1]))
        self.plotafterdelayapplied()
        self.splice_plot()
    def plotafterdelayapplied(self):
        for i,cle in enumerate(self.corr_le):
            self.delays_to_beapplied[i+1]=np.float(cle.text())
        self.vertdelay_w = MatplotlibWidget(size=(22.0, 1.5), dpi=100  ) 
        self.verticalDelayCorrScroll.setWidget(self.vertdelay_w)
        ax=self.vertdelay_w.getFigure().add_subplot(1,1,1)
        for i,d in enumerate(self.flt_logs[self.depthcol_name]):
            try:
                ax.plot(d-self.delays_to_beapplied[i],self.flt_logs[self.logname][i])
            except:
                print('Bad input...')
        
    def doVCorrelation(self):        
        print('Doing vertical correlations')
        self.verticalDelayCorrPanel()

    def splice_logs(self):
        self.sampling_int=np.float(self.sampling_inteval.text())
        self.spliced_logs,self.lognames=splice_w_delay(self.flt_logs,self.delays_to_beapplied,logstep=self.sampling_int,depthcol_name=self.depthcol_name)
        self.display_splice=True
        self.splice_plot()
    def splice_plot(self):
        self.splicew = MatplotlibWidget(size=(22.0, 1.5), dpi=100  ) 
        self.splicedisplayscroll.setWidget(self.splicew)
        if self.display_splice:
            ax=self.splicew.getFigure().add_subplot(1,1,1)
            indx=np.where(self.lognames==self.logname)[0][0]+1
            ax.plot(self.spliced_logs[:,0],self.spliced_logs[:,indx])
        # np.save('spliced_logs.npy',(spliced_logs,lognames))    

        # plot_logs(spliced_logs,lognames)

        # spliced_logs,lognames=np.load('spliced_logs.npy')
    def export(self):       
        self.status_label.setText('Exporting....') 
        las_export(self.spliced_logs,self.lognames,las_file_path)   
        self.status_label.setText('Export success with {} sampling interval. File path is {}'.format(self.sampling_int,las_file_path))
    def get_category(self,log_mnemo,cat_dict):
        #     filewords=multi_split(file_str,delims=['_','-','.'])
            for key in cat_dict:
                if log_mnemo in cat_dict[key]:
                    return key
            return 'NA'
    def histFilter(self):
        # self.depthcol_name='DEPTH'
        self.filtw = MatplotlibWidget(size=(22.0, 1.5), dpi=100  ) 
        self.filtscrollArea.setWidget(self.filtw)
        
        ax=self.filtw.getFigure().add_subplot(1,1,1)
        
        

        hist_bins=np.int(self.n_hist_segments_le.text())
        n_big_patches=np.int(self.n_patches2retain_le.text())

        self.flt_logs[self.logname]=[[]]*len(self.log_bundle)

        log_cate=self.get_category(self.logname,self.type_dict)
        if(log_cate in ['LLD','LLS','MSFL']):
            self.is_resistivityCurve=True
        else:
            self.is_resistivityCurve=False

        for i,lb in enumerate(self.log_bundle):
            if self.is_resistivityCurve:
                logdata=lb[self.logname].copy()
                logdata[logdata==0]=0.001
                logdata=np.log10(logdata)
            else:
                logdata=lb[self.logname].copy()
            self.flt_logs[self.logname][i]=hist_filter(logdata,n_big_patches=n_big_patches,hist_bins=hist_bins)
            ax.plot(lb[self.depthcol_name],self.flt_logs[self.logname][i])
        # print(flt_arrs)
        self.plotafterdelayapplied()
        self.display_splice=False

         
    def filtrt_logs(self,log_bundle,depthcol_name='DEPTH',n_big_patches=1,hist_bins=600):
        flt_logs={}
    # dt=0    
        flt_logs[depthcol_name] =[lb[depthcol_name] for lb in log_bundle]
        for logname in log_bundle[0]['keys']:
            # print(logname)
            flt_logs[logname]=[[] for i in range(len(log_bundle))]
        
        for i,lb in enumerate(log_bundle):            
            for logname in lb['keys']:
                print(logname)
                log_cate=self.get_category(logname,self.type_dict)
                print(log_cate)
                if(log_cate in ['LLD','LLS','MSFL']):
                    self.is_resistivityCurve=True
                else:
                    self.is_resistivityCurve=False

                
                if self.is_resistivityCurve:
                    logdata=lb[logname].copy()
                    logdata[logdata==0]=0.001
                    logdata=np.log10(logdata)
                else:
                    logdata=lb[logname].copy()

                flt_logs[logname][i]=hist_filter(logdata,n_big_patches=n_big_patches,hist_bins=hist_bins)
        return flt_logs
    def run_mass_filter(self):
        hist_bins=np.int(self.n_hist_segments_le.text())
        n_big_patches=np.int(self.n_patches2retain_le.text())    
        self.flt_logs=self.filtrt_logs(self.log_bundle,depthcol_name=self.depthcol_name,n_big_patches=n_big_patches,hist_bins=hist_bins)
        # for i,lb in enumerate(self.log_bundle):            
        #     for logname in lb['keys']:
        #         self.flt_logs[logname][i]=hist_filter(lb[logname].copy(),n_big_patches=n_big_patches,hist_bins=hist_bins)
       
    def logPlotPanel(self):
        print('Initiating plot widget...')
        try:
            self.logname=self.lastree.tree.selectedItems()[0].text(0)
        except:
            self.logname='GR'
        
        # self.depthcol_name='DEPTH'
        # firstlog
        logdata=[]
        depthdata=[]
        self.mw = MatplotlibWidget(size=(22.0, 1.5), dpi=100  ) 
        self.logscrollArea.setWidget(self.mw)
        self.ax=self.mw.getFigure().add_subplot(1,1,1)

        self.filtw = MatplotlibWidget(size=(22.0, 1.5), dpi=100  ) 
        self.filtscrollArea.setWidget(self.filtw)
        ax2=self.filtw.getFigure().add_subplot(1,1,1)
        
        for i,lb in enumerate(self.log_bundle):
            # print(lb[self.logname],lb[self.depthcol_name]) 
            try:
                self.ax.plot(lb[self.depthcol_name],lb[self.logname])
                ax2.plot(lb[self.depthcol_name],self.flt_logs[self.logname][i])
            except:
                print('Log not present')
        
        self.plotafterdelayapplied()
        self.splice_plot()

    def log_correlations_plot(self):
        self.mw = MatplotlibWidget(size=(22.0, len(self.interestedLognames)*1.0), dpi=100)   
        self.logscrollArea.setWidget(self.mw)
        self.mw.setMaximumHeight(100)
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
        # print(dir(self.lastree.tree))
        # print(help(self.lastree.tree.itemAt))
        # print(self.lastree.tree.itemAt(1,0).text(0))
        

        
        
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
    mainWin = VerticalCorrNSplice()   

    mainWin.buildLogTree()

    mainWin.show()
    sys.exit(app.exec_())