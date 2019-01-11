import sys

# from PyQt5.QtGui import 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QTreeWidget,QTreeWidgetItem,QApplication,QMainWindow,
QHBoxLayout,QWidget,QPushButton,QTreeWidgetItemIterator)

class Pytree(QMainWindow): 
    def __init__(self,parent=None):
        super(Pytree,self).__init__(parent)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle('Dynamic Categorizer')
        self.setMinimumWidth(600)
        self.removedmnemonicdict={}        
        self.layout = QHBoxLayout(self.centralWidget)

        self.setLayout(self.layout)
        self.tree=QTreeWidget()
        self.layout.addWidget(self.tree)

        self.select_btn= QPushButton("Select")
        self.layout.addWidget(self.select_btn)
        

        # self.treeview_dict={
        #     'MD':{
        #         'LWD':{
        #             'file4':['200-500','43','gr mfs'],
        #             'file5':['300-450','54','gr mfs']
        #         },
        #         'WireLine':{
        #             'file6':['450-670','2','gr mfs']
        #         }

        #     },
        #     'TVD':{
        #         'LWD':{
        #             'file1':['123-789','45','gr mfs'],
        #             'file2':['234-456','23','gr mfs']
        #         },
        #         'WireLine':{
        #             'file3':['124-789','12','gr mfs']
        #         }

        #     }
            
        # }
        # self.treeview_dict={'MD': {'LWD': {'W2_17in_APWD-Time_LAS.las': ["('465.29', '340.99')", '5', ''], 'W2_8in_Pilot_VISION_Resistivity_APWD_TIME_LAS.LAS': ["('118.14', '501.29')", '5', ''], 'W2_8in_Pilot_VISION_Resistivity_MD_LAS.LAS': ['(119.7864, 503.9868)', '5', 'GR,LLD,LLS,MSFL'], 'W2_VISION_RESISTIVITY-APWD_17in_RM_500-1445m.las': ['(499.872, 1445.2092)', '5', 'GR,LLD,LLS,MSFL']}, 'WireLine': {'W2_12in_DLIS_1430-3100m.las': ['(1429.9692, 3099.9684)', '5', 'GR,LLD,LLS,MSFL,RHOB,NPHI']}}, 'TVD': {}}
        # # item    = QTreeWidgetItem()
    
    def buildTree(self,checkableitemnames=[]):    
        self.tree.headerItem().setText(0, "File name")
        self.tree.headerItem().setText(1, "Depth Range")
        self.tree.headerItem().setText(2, "No of useful Logs")
        self.tree.headerItem().setText(3, "Log Names")

        for key in self.treeview_dict:
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, key)
            # parent.setFlags(parent.flags() | Qt.ItemIsTristate )
            parent.setFlags(parent.flags())
            
            for subkey in self.treeview_dict[key]:
                child = QTreeWidgetItem(parent)
                child.setFlags(child.flags()  )
                # child.setFlags(child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                child.setText(0, subkey)
                # child.setCheckState(0, Qt.Unchecked)
                for thirdkey in self.treeview_dict[key][subkey]:
                    subchild = QTreeWidgetItem(child)
                    subchild.setFlags(child.flags()  | Qt.ItemIsUserCheckable)
                    subchild.setText(0, thirdkey)
                    if thirdkey in checkableitemnames:
                        subchild.setCheckState(0, Qt.Checked)
                    else:
                        subchild.setCheckState(0, Qt.Unchecked)

                    #create the checkbox
                    finaldict=self.treeview_dict[key][subkey][thirdkey]
                    subchild.setText(0, thirdkey)
                    # for fourthkey in finaldict:
                    for i,descr in enumerate(finaldict):
                        # if i < 3:
                        subchild.setText(i+1, descr)
                            # subchild.setCheckState(i, Qt.Unchecked)
                        # if i == 3:
                        #     subchild.setText(i, "Any Notes?")
                        #     subchild.setFlags(subchild.flags() | Qt.ItemIsEditable)
        self.tree.expandToDepth(1)
    def set_tree(self,treeview_dict):
        # self.tree.
        self.treeview_dict=treeview_dict
    # def close(self):
    #     return 'hello'

if __name__ == '__main__':
    app     = QApplication (sys.argv)
    treeview_dict={'MD': {'LWD': {'W2_17in_APWD-Time_LAS.las': ["('465.29', '340.99')", '5', ''], 'W2_8in_Pilot_VISION_Resistivity_APWD_TIME_LAS.LAS': ["('118.14', '501.29')", '5', ''], 'W2_8in_Pilot_VISION_Resistivity_MD_LAS.LAS': ['(119.7864, 503.9868)', '5', 'GR,LLD,LLS,MSFL'], 'W2_VISION_RESISTIVITY-APWD_17in_RM_500-1445m.las': ['(499.872, 1445.2092)', '5', 'GR,LLD,LLS,MSFL']}, 'WireLine': {'W2_12in_DLIS_1430-3100m.las': ['(1429.9692, 3099.9684)', '5', 'GR,LLD,LLS,MSFL,RHOB,NPHI']}}, 'TVD': {}}
        
    tree    = Pytree ()    
    tree.set_tree(treeview_dict)
    tree.buildTree()
    tree.show() 
    tree.tree.expandToDepth(1)
    # print(tree.close() )
    sys.exit(app.exec_())
    # main()