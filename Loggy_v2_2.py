from PyQt5.QtCore import QDate, QFile, Qt, QTextStream, QSize
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtGui import (QFont, QIcon, QKeySequence, QTextCharFormat,
        QTextCursor, QTextTableFormat)
from PyQt5.QtGui import QPixmap,QImage,QPainter,QColor,QBrush,QMouseEvent,QPen
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDockWidget,QWidgetItem,
        QScrollArea,QVBoxLayout,QHBoxLayout,QPushButton,QMenu, QFileDialog,QToolBar,
        QFileDialog, QListWidget, QMainWindow, QMessageBox, QTextEdit,QLabel,QWidget,QTreeWidgetItemIterator)
# import other useful ones
import numpy as np
# from PIL.ImageQt import ImageQt
# from scipy.misc.pilutil import toimage
# import lasio
import os
import pyqtgraph as pg
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import time
# From files of app
import dockwidgets_rc
from LasLoadThread import LasLoadThread
from helper import *
from LogPlot import LogPlot
from LasTree import LasTree
from categorize_v2 import Categorize,LogCategorize
from loggy_settings import well_folder, lwdVSwirelineFile, mnomonicsfile
from pytree_adv import Pytree
from LateralCorr_v2 import LateralCorr
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.createActions()
        self.createMenus()
        self.setGeometry(100,100, 600,900)

        self.centralWidget = QWidget()
        # GrphicsWidget()
        layout = QHBoxLayout(self.centralWidget)
        self.scrollArea = QScrollArea(self)
        self.mw = MatplotlibWidget(size=(3.0, 40.0), dpi=100)
        lplot=self.mw.getFigure().add_subplot(121) 
        self.ax=self.mw.getFigure().gca()   
        l, b, w, h = self.ax.get_position().bounds     
        # print(l, b, w, h)
        # self.ax.invert_yaxis()
        self.ax.set_position([0.125,0.05,0.5,0.94])
        
        # l, b, w, h = self.ax.get_position().bounds     
        # print(l, b, w, h)
        self.mw.draw()
        # self.plotlayout.addWidget(self.mw)

        self.scrollArea.setWidget(self.mw)

        layout.addWidget(self.scrollArea)

        self.setCentralWidget(self.centralWidget)
        self.lastree = LasTree()        
        self.logtree = LasTree()
        self.wellLoad()
        self.logtree.set_files(['GR','BS'])
        self.logtree.buildTreeWidget()
        self.logtree.tree.itemSelectionChanged.connect(self.logPlot)

        self.createDockWindows()
        
        # self.logFileList.itemSelectionChanged.connect(self.lasLoad)
        # if not self.las_just_selected:
        # self.logList.itemSelectionChanged.connect(self.logPlot)


        self.setWindowTitle("Loggy")

        # self.newLetter()
    def wellLoad(self):
        self.wellFolder=well_folder
        
        self.files=[]
        for f in np.array(os.listdir(self.wellFolder)[:]):
            if f[-4:].lower() in ['.las','dlis']:
                self.files.append(f)
        self.files=np.array(self.files)
        files_w_path=[self.wellFolder+f for f in self.files]

        cols=[]

        # self.files=np.array(os.listdir(self.wellFolder)[:])
        
        self.lastree.set_files(self.files)
        self.lastree.buildTreeWidget()
        self.lasfiletree=self.lastree.treeview_dict.copy()
        self.lastree.tree.itemSelectionChanged.connect(self.lasLoad)
        


        self.lasLoadThread = LasLoadThread(files=files_w_path)
    # def lasBackgroundLoad():
        

    def lasLoad (self):        
        las_name=self.lastree.tree.selectedItems()[0].text(0) #self.logFileList.selectedItems()[0].text() 
        if las_name in ['TVD','MD','LWD','WireLine']:
            return      

        findex=np.where(self.files==las_name)[0][0]
        # print(findex)
        Loaded=False
        while(not Loaded):
            if(findex<len(self.lasLoadThread.Lases)):
                self.las=self.lasLoadThread.Lases[findex]
                Loaded=True
                self.logtree.tree.clear()
                # print('hi')
            else:
                # print('hello')
                
                # self.logtree.addItems(['Loading....'])
                time.sleep(1)
        
        if len(self.logtree.tree.selectedItems())>0:
            item = self.logtree.tree.selectedItems()[0]
            # print(dir(item))
            item.setSelected= False
        if not (len(self.las.keys())<1):
            # self.logtree = LasTree(self.las.keys())
            self.logtree.set_files(self.las.keys())
            self.logtree.buildTreeWidget()
 
            dcol=self.las.keys()[find_depth_indx(self.las)]
            self.depth_col=str_array2floats(self.las[dcol])
        # else:
            
        
        # self.las_just_selected = True

        
        
    def logPlot(self):
        
        # print(self.mw.getFigure().)
        # pass
        # if not self.las_just_selected:
        if len(self.logtree.tree.selectedItems())>0:
            keycol=self.logtree.tree.selectedItems()[0].text(0)
            try:
                self.log_col=str_array2floats(self.las[keycol])            
                self.ax=LogPlot.basicPlot(self.ax,self.depth_col,self.log_col,lcolor='#800000')
                self.ax.set_ylim(500,3000)
                self.ax.invert_yaxis()
            except:
                print('Unable to convert log to floats')
        self.mw.draw()
    def set_category(self):
        # qt_app = QApplication(sys.argv)
        # mnomonicsfile=mnomonicsfile
        # print(self.logtree.treeview_dict)
        # set_category_app = Categorize(self.logtree.treeview_dict,mnomonicsfile)
        print('*************************************************')
        print(self.logtree.treeview_dict)
        category_window = Categorize(self)
        category_window.set_params(self.logtree,mnomonicsfile)
        category_window.show()

        # self.logtree.tree.clear()
        # self.logtree.buildTreeWidget()
        # set_category_app.run()
        # self.logtree.buildTreeWidget()


    def createDockWindows(self):
        
        dock = QDockWidget("Log Files", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(self.lastree.tree)
        # 
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self.set_category_button = QPushButton('Set Category', self)
        self.slect_files_button = QPushButton('Select files for further process', self)

        # self.layout.addWidget(self.logtree.tree)
        dock = QDockWidget("Set", self)
        btn_w=QWidget()
        self.btn_layout=QVBoxLayout()
        btn_w.setLayout(self.btn_layout)
        dock.setWidget(btn_w)

        self.btn_layout.addWidget(self.set_category_button)
        self.btn_layout.addWidget(self.slect_files_button)

        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        dock = QDockWidget("Logs", self)

        
        dock.setWidget(self.logtree.tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        self.set_category_button.clicked.connect(self.set_category)
        self.slect_files_button.clicked.connect(self.retain4FurtherAnalysis)
    def createActions(self):
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)
        self.openFileAct = QAction("&Open", self, shortcut="Ctrl+O",
                triggered=self.file_open)
        self.aboutAct = QAction("&About", self, triggered=self.about)

    def retain4FurtherAnalysis(self):
        # print(self.lastree.treeview_dict)
        
        print(self.lasfiletree)
        lasfilemodtree={}
        lc=LogCategorize(mnomonicsfile)
        self.files_4_further_analysis=[]
        self.allfiles={'fname':[],'drange':[],'curve_names':[]}
        if len(self.lasLoadThread.Lases)==len(self.files):
            print('Loaded all files...')
            for las,lf in zip(self.lasLoadThread.Lases,self.files):            
                lc.set_las(las)
                lc.lasCategorize()
                # print(lc.treeview_dict)
                # print(lc.get_catePresent())
                # print( lc.get_lasdepthrange())
                # print( lc.get_curverange('CAL'))
                lcates=lc.get_catePresent()
                # if len(lcates)>3:
                self.allfiles['fname'].append(lf)
                self.allfiles['drange'].append( lc.get_lasdepthrange())
                self.allfiles['curve_names'].append( lc.get_catePresent())
            # print(self.allfiles)
            topdepts = np.array([np.float(d[0]) for d in self.allfiles['drange']])
            ncurves = np.array([len(d) for d in self.allfiles['curve_names']])
            
            self.allfiles['topdepts']=topdepts
            self.allfiles['ncurves']=ncurves
            self.allfiles['fname']=np.array(self.allfiles['fname'])
            print(np.column_stack((topdepts,ncurves)))
            for k in self.lasfiletree:
                lasfilemodtree[k]={}
                for l in self.lasfiletree[k]:
                    lasfilemodtree[k][l]={}
                    if(len(self.lasfiletree[k][l])>0):
                        branch_files=np.array(self.lasfiletree[k][l])     
                        print('*****************************************')
                        print(branch_files)  
                        branch_files=self.sort_per_depthNcurves(branch_files)   
                        print(branch_files)  
                        for m in branch_files:     
                            indx=np.where(self.allfiles['fname']==m)[0][0]
                            print(m,self.allfiles['fname'],indx)
                            lasfilemodtree[k][l][m]=['{} - {}'.format(*self.allfiles['drange'][indx]), str(len(self.allfiles['curve_names'][indx])), ','.join(self.allfiles['curve_names'][indx])]
        else:
            print('Not loaded all files...')
        print(lasfilemodtree)
        self.retain_tree    = Pytree(self) 
        self.retain_tree.set_tree(lasfilemodtree)
        self.retain_tree.select_btn.clicked.connect(self.return_selected_items)
        self.retain_tree.buildTree()
        self.retain_tree.show() 

        # sys.exit(app.exec_())
    def return_selected_items(self):
        iterator = QTreeWidgetItemIterator(self.retain_tree.tree )
        value = iterator.value()
        self.retain_files=[]
        self.retain_files_ranges=[]
        while value:
            if value.checkState(0) == Qt.Checked:
                # print('yes')
                print(value.text(0))
                self.retain_files.append(value.text(0))
                self.retain_files_ranges.append(value.text(1))
            # if hasattr(value, 'saveValue'):
            #     value.saveValue()
            iterator += 1
            value = iterator.value()
        # print(self.retain_files)
        # print(self.retain_files_ranges)
        self.retain_tree.close()
        self.show_lateralCorrections()
    def show_lateralCorrections(self):       
        
        self.lateralCorr_buttons=[]
        for i,rf in enumerate(zip(self.retain_files,self.retain_files_ranges)):
            lcw=QWidget()
            self.harlayout=QHBoxLayout()
            self.lateralCorr_buttons.append( QPushButton('Do Lateral Depth Match-'+str(i), self))
            self.harlayout.addWidget(QLabel(rf[1]))
            self.harlayout.addWidget(self.lateralCorr_buttons[-1])
            print(rf[0])
            self.lateralCorr_buttons[-1].clicked.connect(lambda state, x=rf[0]: self.doLateralCorr(x) )     
            lcw.setLayout(self.harlayout)   
            self.btn_layout.addWidget(lcw)

    def doLateralCorr(self,lfilename):
        self.selected_lases=[]   
        findex=np.where(self.files==lfilename)[0][0]
        print(lfilename,findex)
        self.selected_lases.append(self.lasLoadThread.Lases[findex])
        lateralWin = LateralCorr(self)
        lateralWin.buildLogTree(self.selected_lases)
        lateralWin.logCorrelations()
        lateralWin.show()
    def sort_per_depthNcurves(self,branch_files) :
        indxs=[]
        
        for m in branch_files:     
            indxs.append(np.where(self.allfiles['fname']==m)[0][0])
        ncurves=self.allfiles['ncurves'][indxs]

        sort_dpt_indx=np.argsort(self.allfiles['topdepts'][indxs])

        ncurves_rule=ncurves[sort_dpt_indx]>2
        branch_files=branch_files[sort_dpt_indx]
        
        
        # sort_dpt_indx=sort_dpt_indx[::-1]

        return np.append(branch_files[ncurves_rule],branch_files[~ncurves_rule])



    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        # self.fileMenu.addAction(self.openAct)
        # self.fileMenu.addAction(self.printAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openFileAct)
        self.fileMenu.addAction(self.exitAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        # self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.fileMenu)
        # self.menuBar().addMenu(self.viewMenu)
        # self.menuBar().addMenu(self.digitizeMenu)
        self.menuBar().addMenu(self.helpMenu)

        self.file_toolbar = QToolBar("File")
        self.file_toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.file_toolbar)
    def about(self):
        QMessageBox.about(self, "About Log splicer",
            "<p>The <b>Image Viewer</b> example shows how to combine "
                        "(QScrollArea.widgetResizable), can be used to implement "
            "zooming and scaling features.</p>"
            "<p>In addition the example shows how to use QPainter to "
            "print an image.</p>")
    def file_open(self):
        print('Not yet set')


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
