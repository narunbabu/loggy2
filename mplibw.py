from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        mw = MatplotlibWidget()
        subplot = mw.getFigure().add_subplot(111)
        mw.draw()
        # print(dir(mw))
        # layout=QHBoxLayout()
        # mylabel=QLabel('Hi')
        # layout.addWidget(mylabel)
        # layout.addWidget(mw)
        # self.setLayout(layout)


        layout = QFormLayout()
        self.btn = QPushButton("Choose from list")
        self.btn.clicked.connect(self.getItem)
            
        self.le = QLineEdit()
        layout.addRow(self.btn,self.le)
        self.btn1 = QPushButton("get name")
        self.btn1.clicked.connect(self.gettext)
            
        self.le1 = QLineEdit()
        layout.addRow(self.btn1,self.le1)
        self.btn2 = QPushButton("Enter an integer")
        self.btn2.clicked.connect(self.getint)
            
        self.le2 = QLineEdit()
        layout.addRow(self.btn2,self.le2)
        self.setLayout(layout)
        self.setWindowTitle("Input Dialog demo")

        layout.addRow(mw)

    def getItem(self):
        items = ("C", "C++", "Java", "Python")
            
        item, ok = QInputDialog.getItem(self, "select input dialog", 
            "list of languages", items, 0, False)
                
        if ok and item:
            self.le.setText(item)
			
    def gettext(self):
        text, ok = QInputDialog.getText(self, 'Text Input Dialog', 'Enter your name:')
            
        if ok:
            self.le1.setText(str(text))
			
    def getint(self):
        num,ok = QInputDialog.getInt(self,"integer input dualog","enter a number")
            
        if ok:
            self.le2.setText(str(num))
if __name__ == '__main__':
    
    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())