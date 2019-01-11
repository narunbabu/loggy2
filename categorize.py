from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from LasTree import treeWidgetFrmDict,get_txtdict,write_txtdict
# from LasTreeimport get_txtdict as getlogdict
qt_app = QApplication(sys.argv)
# def write_txtdict(file,delimiter=','):
#             with open(file,'w') as f:
#                 lines=f.writelines()
#                 file_dict={}
#                 for l in lines:
#                     [key,val]=l.split('=')
#                     file_dict[key.strip()]=[v.strip() for v in val.split(delimiter)]
#             return file_dict

class Categorize(QMainWindow):

    def __init__(self,category_dict,mnemonicsfile):

        QMainWindow.__init__(self)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle('Dynamic Categorizer')
        self.setMinimumWidth(600)
        self.removedmnemonicdict={}
        
        # self.logs=logs
        self.mnemonicsfile=mnemonicsfile
        self.base_categories=get_txtdict(self.mnemonicsfile,delimiter=' ')
        print(self.base_categories)
        self.logs=category_dict['Log']['NA']
        self.category_dict=category_dict
        for bkey in self.base_categories.keys():
            self.removedmnemonicdict[bkey]=[]
            if bkey not in category_dict['Log'].keys():
                self.category_dict['Log'][bkey]=[]                
        del self.category_dict['Log']['NA']

 
        # Create the QVBoxLayout that lays out the whole form
        self.layout = QHBoxLayout(self.centralWidget)

        self.listlogw=QListWidget()
        self.listlogw.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listlogw.addItems(self.logs)
        self.catelogsw=QTreeWidget() 
        print(self.category_dict)
        self.catelogsw=  treeWidgetFrmDict(self.catelogsw,self.category_dict)
        self.loglayout = QVBoxLayout()
        self.loglayout.addWidget(self.listlogw)
        self.catelogslayout = QVBoxLayout()
        self.catelogslayout.addWidget(self.catelogsw)

        self.deset_button = QPushButton('<', self)
        self.set_button = QPushButton('>', self)
        self.save_button = QPushButton('Save changes', self)
        self.buttonslayout = QVBoxLayout()
        self.buttonslayout.addWidget(self.set_button)
        self.buttonslayout.addWidget(self.deset_button)

        self.layout.addLayout(self.loglayout)        
        self.layout.addLayout(self.buttonslayout)
        self.layout.addLayout(self.catelogslayout)
        self.layout.addWidget(self.save_button)


        self.setLayout(self.layout)



        self.set_button.clicked.connect(self.setLog2Category)
        self.deset_button.clicked.connect(self.desetLog2Category)
        self.save_button.clicked.connect(self.update_basecategories)
    
    def setLog2Category(self):
        # print(self.listlogw.selectedItems())
        # print(self.catelogsw.selectedItems())
        if (len(self.catelogsw.selectedItems())<1) |(len(self.listlogw.selectedItems())<1):
            return
        category=self.catelogsw.selectedItems()[0].text(0)
        log_labels=[llist.text() for llist in self.listlogw.selectedItems()]
        self.category_dict['Log'][category]=log_labels
        self.catelogsw.clear()
        print(self.category_dict)
        self.catelogsw=  treeWidgetFrmDict(self.catelogsw,self.category_dict)
        for litem in self.listlogw.selectedItems():
            # for SelectedItem in self.ListDialog.ContentList.selectedItems():
            self.listlogw.takeItem(self.listlogw.row(litem))

            # item = self.listlogw.takeItem(self.listlogw.currentRow())
            # item = None
            # litem.remove()
        for l in log_labels:
            if l in self.removedmnemonicdict[category]:
                self.removedmnemonicdict[category].remove(l)

        
        # self.category_dict

    def desetLog2Category(self):
        if len(self.catelogsw.selectedItems())<1:
            return
        toberemoved=self.catelogsw.selectedItems()[0].text(0)
        
        for key in self.category_dict['Log']:
            if toberemoved in self.category_dict['Log'][key]:
                self.category_dict['Log'][key].remove(toberemoved)
                self.removedmnemonicdict[key].append(toberemoved)
        # self.category_dict=[llist.text() for llist in self.listlogw.selectedItems()]
        self.catelogsw.clear()
        self.catelogsw=  treeWidgetFrmDict(self.catelogsw,self.category_dict)
        self.listlogw.addItem(toberemoved)
    def update_basecategories(self):
        print('Saved') 
        print(self.base_categories)     
        for key in self.category_dict['Log']:
            for log in self.category_dict['Log'][key]:
                if not log in self.base_categories[key]:
                    self.base_categories[key].append(log)
        for key in self.removedmnemonicdict:
            for log in self.removedmnemonicdict[key]:
                if log in self.base_categories[key]:
                    self.base_categories[key].remove(log)
                    self.removedmnemonicdict[key].remove(log)      
        print(self.base_categories)              
        write_txtdict(self.mnemonicsfile,self.base_categories,delimiter=' ')
        self.close()
        
    def run(self):
        # Show the form
        self.show()
        # Run the qt application
        qt_app.exec_()
 
# Create an instance of the application window and run it

# treeview_dict={'Log': {'GR': ['GR_ARC'], 'RHOB': ['RHOB', 'ROBB'], 'NPHI': ['TNPH'], 'NA': ['DEPT', 'ROP5_RM', 'A16H', 'A22H', 'A28H', 'A34H', 'A40H', 'P16H', 'P22H', 'P28H', 'P34H', 'P40H', 'A16L', 'A22L', 'A28L', 'A34L', 'A40L', 'P16L', 'P22L', 'P28L', 'P34L', 'P40L', 'ECD_ARC', 'APRS_ARC', 'ATMP', 'DRHO', 'DRHB', 'DCHO', 'DCVE', 'DCAV', 'VERD', 'HORD']}}
# logs=['GR_ARC','RHOB', 'ROBB','TNPH','DEPT', 'ROP5_RM', 'A16H', 'A22H', 'A28H', 'A34H', 'A40H', 'P16H', 'P22H', 'P28H', 'P34H', 'P40H', 'A16L', 'A22L', 'A28L', 'A34L', 'A40L', 'P16L', 'P22L', 'P28L', 'P34L', 'P40L', 'ECD_ARC', 'APRS_ARC', 'ATMP', 'DRHO', 'DRHB', 'DCHO', 'DCVE', 'DCAV', 'VERD', 'HORD']
# # base_categories=get_txtdict(r'D:\Ameyem Office\Projects\Cairn/mnemonics.txt',delimiter=' ')
# mnomonicsfile=r'D:\Ameyem Office\Projects\Cairn/mnemonics.txt'
# # print(base_categories)
# # # inputtree_dict=treeview_dict.copy()
# # uncatelogs=treeview_dict['Log']['NA']
# # for bkey in base_categories.keys():
# #     if bkey not in treeview_dict.keys():
# #         treeview_dict[bkey]=[]
        
# # del treeview_dict['Log']['NA']
# # print(inputtree_dict)
# app = Categorize(treeview_dict,mnomonicsfile)
# app.run()

