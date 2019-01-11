from PyQt5.QtCore import QRect, QSize, QDir, Qt,QPointF,QRectF
from PyQt5.QtGui import QImage, QPainter, QPalette, QPixmap, QColor,QIcon

from PyQt5.QtWidgets import (QAction, QApplication, QFrame, QFileDialog, QLabel,QLayout,QToolBar,
        QMainWindow, QMenu, QMessageBox, QScrollArea, QSizePolicy,QInputDialog,QHBoxLayout,
        QPushButton,QLineEdit,QListWidget,QListWidgetItem,QGridLayout,QWidget,QGraphicsItem ,QWidgetItem,QTextBrowser)

import pyqtgraph as pg
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import numpy as np
import pandas as pd
import os
from vesinv_fns import *

class ItemWrapper(object):
    def __init__(self, i, p):
        self.item = i
        self.position = p


class BorderLayout(QLayout):
    West, North, South, East, Center = range(5)
    MinimumSize, SizeHint = range(2)

    def __init__(self, parent=None, margin=None, spacing=-1):
        super(BorderLayout, self).__init__(parent)

        if margin is not None:
            self.setContentsMargins(margin, margin, margin, margin)

        self.setSpacing(spacing)
        self.list = []

    def __del__(self):
        l = self.takeAt(0)
        while l is not None:
            l = self.takeAt(0)

    def addItem(self, item):
        self.add(item, self.West)
    # def addItemEast(self, item):
    #     self.add(item, self.East)

    # def addWidget(self, widget, position):
    #     self.add(QWidgetItem(widget), position)

    def expandingDirections(self):
        return Qt.Horizontal | Qt.Vertical

    def hasHeightForWidth(self):
        return False

    def count(self):
        return len(self.list)

    def itemAt(self, index):
        if index < len(self.list):
            return self.list[index].item

        return None

    def minimumSize(self):
        return self.calculateSize(self.MinimumSize)

    def setGeometry(self, rect):
        center = None
        eastWidth = 0
        westWidth = 1
        northHeight = 0
        southHeight = 0
        centerHeight = 0

        super(BorderLayout, self).setGeometry(rect)

        for wrapper in self.list:
            item = wrapper.item
            position = wrapper.position
            if position == self.Center:
                center = wrapper

        centerHeight = rect.height() - northHeight - southHeight

        for wrapper in self.list:
            item = wrapper.item
            position = wrapper.position

            if position == self.West:
                item.setGeometry(QRect(rect.x() + westWidth,
                        northHeight, item.sizeHint().width()+105, centerHeight))   
                # print(item.sizeHint().width()) 

                westWidth += item.geometry().width() + self.spacing()


        if center:
            center.item.setGeometry(QRect(westWidth, northHeight,
                    rect.width() - eastWidth - westWidth, centerHeight))

    def sizeHint(self):
        return self.calculateSize(self.SizeHint)

    def takeAt(self, index):
        if index >= 0 and index < len(self.list):
            layoutStruct = self.list.pop(index)
            return layoutStruct.item

        return None

    def add(self, item, position):
        self.list.append(ItemWrapper(item, position))

    def calculateSize(self, sizeType):
        totalSize = QSize()

        for wrapper in self.list:
            position = wrapper.position
            itemSize = QSize()

            if sizeType == self.MinimumSize:
                itemSize = wrapper.item.minimumSize()
            else: # sizeType == self.SizeHint
                itemSize = wrapper.item.sizeHint()

            if position in (self.North, self.South, self.Center):
                totalSize.setHeight(totalSize.height() + itemSize.height())

            if position in (self.West, self.East, self.Center):
                totalSize.setWidth(totalSize.width() + itemSize.width())

        return totalSize


class VESViewer(QMainWindow):
    curve=[]
    Image=[]
    listitem=[]
    imfolder=r"D:\Ameyem Office\Geoservices\Digitizer\\"
    zoom_fact=1
    fileName=''
    pick_type='digitize'
    depth_pix_lims=[]
    prop_pix_lims=[]
    init_thicks=[1,10,15,175]
    init_res=[20,4,60,200,2000]
    proj_path=r'D:/Ameyem Office/Projects/Electric surveys/Easwar files/Mahoba/mohaba.resp/'
        
    
    def __init__(self):
        super(VESViewer, self).__init__()

        self.createActions()
        self.createMenus()
        win = QWidget()
        self.setCentralWidget(win)
        self.plotlayout = QHBoxLayout(self) 
        self.init_m=np.append(self.init_res ,self.init_thicks)
        self.datapath = self.proj_path+'VESData/'
        # creates plot
        # self.plot = pg.PlotWidget()
        self.mw = MatplotlibWidget()
        self.subplot1 = self.mw.getFigure().add_subplot(121)
        self.subplot2 = self.mw.getFigure().add_subplot(122)
        self.mw.draw()
        self.plotlayout.addWidget(self.mw)
        # mltoolbar=self.mw.get_ToolBar()

        layout = BorderLayout()

        layout.add(self.plotlayout, BorderLayout.Center)
        


        self.list_w =QListWidget()
        # self.listitem.append(QListWidgetItem('Welcome to ResLayer!!!'))
        self.list_w.setFrameStyle(QFrame.Box | QFrame.Raised)
        layout.add(QWidgetItem(self.list_w), BorderLayout.West)
        win.setLayout(layout)
        # self.list_w.addItem(self.listitem[0])
        # self.list_w.itemClicked.connect(self.OnSingleClick)
        self.list_w.itemSelectionChanged.connect(self.OnSingleClick)

        self.setWindowTitle("Border Layout")

        mypen = pg.mkPen('y', width=1)
        # self.curve = self.plot.plot(x=[], y=[], pen=mypen)
        # self.plot.addItem(self.curve)
        
        files=os.listdir(self.datapath)
        for f in files:
            self.listitem.append(QListWidgetItem(f[:-4]))
            self.list_w.addItem(self.listitem[-1])
        
        self.vdf= pd.read_csv(self.datapath+files[0],header=None)
        self.plotVES()

    def onMouseMoved(self, point):
        # print(point)
        p = self.plot.plotItem.vb.mapSceneToView(point)
        self.statusBar().showMessage("{}-{}".format(p.x(), p.y()))
    def about(self):
        QMessageBox.about(self, "About Image Viewer",
            "<p>The <b>Image Viewer</b> example shows how to combine "
                        "(QScrollArea.widgetResizable), can be used to implement "
            "zooming and scaling features.</p>"
            "<p>In addition the example shows how to use QPainter to "
            "print an image.</p>")
    def dialog_critical(self, s):
        dlg = QMessageBox(self)
        dlg.setText(s)
        dlg.setIcon(QMessageBox.Critical)
        dlg.show()
        
    def file_open(self):
        # path, _ = QFileDialog.getOpenFileName(self, "Open file", "", "CSV documents (*.dat);All files (*.*)")
        path=r'D:/Ameyem Office/Projects/Electric surveys/Easwar files/Mahoba/VES_data/112.dat'
        try:
            self.vdf=pd.read_csv(path,header=None)
            
        except Exception as e:
            self.dialog_critical(str(e))

        else:
            self.path = path
            self.plotVES(self.vdf)

        
    def createActions(self):
        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)
        self.openFileAct = QAction("&Open", self, shortcut="Ctrl+O",
                triggered=self.file_open)
        self.aboutAct = QAction("&About", self, triggered=self.about)     


        self.do_inversion_action = QAction(QIcon(os.path.join('ves_imgs', 'invert-tool.png')), "&Invert", self,shortcut="Ctrl+I",
        triggered=self.doVESinv)
        self.do_inversion_action.setStatusTip("Run inversion")
        # self.do_inversion_action.triggered.connect(self.doVESinv)
        

        # openFileAct = QAction(QIcon(os.path.join('images', 'blue-folder-open-document.png')), "Open file...", self)
        # open_file_action.setStatusTip("Open file")
        # open_file_action.triggered.connect(self.file_open)
        # file_menu.addAction(open_file_action)
        # file_toolbar.addAction(open_file_action)
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

        self.fileMenu.addAction(self.do_inversion_action)
        self.file_toolbar.addAction(self.do_inversion_action)

    def OnSingleClick(self):
        print('\nItems selected...',end=' ')
        # self.curve=self.plot.plot(x=[0.9 ,300], y=[1, 10000], size=1, pen=pg.mkPen(None),clear=True)
        # self.plot2.plot(x=[0.9 ,300], y=[1, 10000], size=1, pen=pg.mkPen(None),clear=True)
        for item in self.list_w.selectedItems():
            vespoint_name=item.text()
            print(vespoint_name, end=' ')
            self.vdf=pd.read_csv(self.datapath+vespoint_name+'.dat',header=None)
            
        # # self.plot.close()
        # # self.plot = pg.PlotWidget()
            self.plotVES()
        # self.plotLocationPanel(locations4panel)
    def plotVES(self):
        # self.curve=
        self.subplot1.cla()
        self.subplot1.loglog(self.vdf[0],self.vdf[1],'*', basex=10)
        # self.subplot1.grid(True)
        self.subplot1.grid(b=True, which='major', color='grey', linestyle='-')
        self.subplot1.grid(b=True, which='minor')
        self.subplot1.set_title('Apparent resisitivity log ')
        self.subplot1.set_xlabel('Distance (m)')
        self.subplot1.set_ylabel('Apparent Resistivity (ohm-m)')
        self.subplot1.set_xlim(1,1000)
        self.subplot1.set_ylim(1,10000)

        self.subplot2.cla()
        # self.subplot2.loglog(self.vdf[0],self.vdf[1],'*', basex=10)
        # self.subplot1.grid(True)
        lr=int(1+len(self.init_m)/2)
        lt=int(len(self.init_m)/2)
        r = np.append(self.init_m[:lr],np.nan);
        t = np.append(np.append(0.01,self.init_m[-lt:]),1000);

        self.subplot2.grid(b=True, which='major', color='grey', linestyle='-')
        self.subplot2.grid(b=True, which='minor')
        self.subplot2.set_title('Layer model')
        self.subplot2.set_xlabel('Resistivity (ohm-m)')
        self.subplot2.set_ylabel('Depth (m)')
        # self.subplot2.invert_yaxis()
        self.subplot2.set_xlim(1,6000)
        self.subplot2.set_ylim(0.1,500)

        self.subplot2.step(r,np.cumsum(t),'k',dashes=[5, 5, 5, 5],linewidth=2)

        self.subplot2.set_xscale('log')
        self.subplot2.set_yscale('log')
        self.subplot2.invert_yaxis()
        self.mw.draw()
            
    def VESInvplot(self,x,roa,roaf,m,mf):
        lr=int(1+len(mf)/2)
        lt=int(len(mf)/2)
        rf = np.append(mf[:lr],np.nan);
        tf = np.append(np.append(0.01,mf[-lt:]),1000);
        self.subplot1.loglog(x,roaf,'-r', basex=10)
        self.subplot2.step(rf,np.cumsum(tf), 'r')

        self.mw.draw()
    def doVESinv(self):
        method='ghosh'
        x = self.vdf[0].values;
        roa = self.vdf[1].values;  
        # ri= [100, 30, 20., 4.];
        # ti =[9, 61 ,50];
        m = np.append(self.init_res ,self.init_thicks)
        mf,roaf=VES1dInv(m,x,roa,method=method,maxiteration=100)
        # VESplot(self.mw,x,roa,roaf,m,mf)
        self.VESInvplot(x,roa,roaf,m,mf)
        # self.VESinvPlot(x,roa,roaf,m,mf)
   

if __name__ == '__main__':
    
    import sys

    app = QApplication(sys.argv)
    vesViewer = VESViewer()
    vesViewer.show()
    sys.exit(app.exec_())
