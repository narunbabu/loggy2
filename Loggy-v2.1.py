from PyQt5.QtCore import QDate, QFile, Qt, QTextStream, QSize
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtGui import (QFont, QIcon, QKeySequence, QTextCharFormat,
        QTextCursor, QTextTableFormat)
from PyQt5.QtGui import QPixmap,QImage,QPainter,QColor,QBrush,QMouseEvent,QPen
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QDockWidget,QWidgetItem,
        QScrollArea,QVBoxLayout,QHBoxLayout,QPushButton,QMenu, QFileDialog,QToolBar,
        QFileDialog, QListWidget, QMainWindow, QMessageBox, QTextEdit,QLabel,QWidget)
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
from categorize_v2 import Categorize
from loggy_settings import well_folder, lwdVSwirelineFile, mnomonicsfile
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

        # self.layout.addWidget(self.logtree.tree)
        dock = QDockWidget("Set", self)
        dock.setWidget(self.set_category_button)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        dock = QDockWidget("Logs", self)

        
        dock.setWidget(self.logtree.tree)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        self.set_category_button.clicked.connect(self.set_category)
    def createActions(self):
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)
        self.openFileAct = QAction("&Open", self, shortcut="Ctrl+O",
                triggered=self.file_open)
        self.aboutAct = QAction("&About", self, triggered=self.about)  

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
