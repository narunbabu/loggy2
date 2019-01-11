from PyQt5.QtCore import Qt,QUrl
from PyQt5 import QtGui
from PyQt5.QtWidgets import (QTreeWidget,QTreeWidgetItem,QApplication)

import os
import numpy as np
from WellTree import *
from SelectionLasFunctions import *
from pytree_adv import *
from SuitSplice import *

def treeWidgetFrmDict(tree,treeview_dict): #QTreeWidgetItem()
        # item    = QTreeWidgetItem()
        j=0
        for i,key in enumerate(treeview_dict):
            
            if len(treeview_dict[key])>0:
                j+=1
                parent = QTreeWidgetItem(tree)
                parent.setText(0, '{}) {} ({})'.format(j,key,len(treeview_dict[key])))
                # parent.setFlags(parent.flags() | Qt.ItemIsTristate )
                parent.setFlags(parent.flags())
                
                for subkey in treeview_dict[key]:
                    child = QTreeWidgetItem(parent)
                    child.setFlags(child.flags()  )
                    # child.setFlags(child.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
                    child.setText(0, subkey)
                # child.setCheckState(0, Qt.Unchecked)
#                 finaldict=treeview_dict[key][subkey]
#                 for thirdkey in finaldict:
#                     subchild = QTreeWidgetItem(child)
#                     subchild.setFlags(child.flags()  ) #| Qt.ItemIsUserCheckable
#                     subchild.setText(0, thirdkey)
                    # subchild.setCheckState(0, Qt.Unchecked)

                    # #create the checkbox
                    # finaldict=self.treeview_dict[key][subkey][thirdkey]
                    # # for fourthkey in finaldict:
                    # for i in range(self.tree.headerItem().columnCount()):
                    #     # if i < 3:
                    #     subchild.setText(i, finaldict[i])
        tree.expandToDepth(1)
        return tree
def makeLikeTree(well_las_attr_dict):
        # treeview_dict={'MD': {'LWD': {'W2_17in_APWD-Time_LAS.las': ["('465.29', '340.99')", '5', ''], 'W2_8in_Pilot_VISION_Resistivity_APWD_TIME_LAS.LAS': ["('118.14', '501.29')", '5', ''], 'W2_8in_Pilot_VISION_Resistivity_MD_LAS.LAS': ['(119.7864, 503.9868)', '5', 'GR,LLD,LLS,MSFL'], 'W2_VISION_RESISTIVITY-APWD_17in_RM_500-1445m.las': ['(499.872, 1445.2092)', '5', 'GR,LLD,LLS,MSFL']}, 'WireLine': {'W2_12in_DLIS_1430-3100m.las': ['(1429.9692, 3099.9684)', '5', 'GR,LLD,LLS,MSFL,RHOB,NPHI']}}, 'TVD': {}}
     
    well_las_attr_dict_tree={'Wells':{}}
    for w in well_las_attr_dict:
        # print(well_las_attr_dict[w])
        if len(well_las_attr_dict[w].keys())>0:
            well_las_attr_dict_tree['Wells'][w]={}
            for fn in well_las_attr_dict[w]:
                lencate=len(well_las_attr_dict[w][fn]['categories'])
                if lencate>0:
                    drangestr=str( well_las_attr_dict[w][fn]['depthrange'])
                    lencurve_str=str(lencate)
                    categories=','.join(well_las_attr_dict[w][fn]['categories'])
                    well_las_attr_dict_tree['Wells'][w][fn]=[drangestr, lencurve_str,categories ]
    return well_las_attr_dict_tree
            

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # self.createActions()
        # self.createMenus()
        self.setGeometry(100,100, 600,900)
        filter = "Wav File (*.wav)"
        dialog = QtGui.QFileDialog(self, 'Well Parent folder', 'D:/', filter)
        dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        # dialog.setSidebarUrls([QUrl.fromLocalFile(place)])
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.parent_path = dialog.selectedFiles()[0]
        print('self.parent_path   ',self.parent_path)
        tree    = QTreeWidget ()
        # parent_path=r'\\172.16.165.171\Team_DM\Well_Data\\'
        # self.parent_path=r'D:\Ameyem Office\Projects\Carn\\'
        self.parent_path=self.parent_path+'\\'
        mnomonicsfile=r'D:\Ameyem Office\Projects\Cairn\mnemonics_revised.txt'
        lf=WellsParent(self.parent_path)
        well_las_dict=lf.LookgetWellLas(extensions=['.las'])
        self.well_las_attr_dict=getLasAttr4wells(well_las_dict,mnomonicsfile)

        self.tree    = Pytree (self)    
        self.tree.set_tree(makeLikeTree(self.well_las_attr_dict))
        autoselectedfiles=self.autoSelectLasFiles()        
        self.tree.buildTree(checkableitemnames=autoselectedfiles)
        self.tree.show() 
        self.tree.tree.expandToDepth(1)
        # print(tree.close() )
        

        self.tree.select_btn.clicked.connect(self.return_selected_items)
        sys.exit(app.exec_())

    def autoSelectLasFiles(self):
        selectedfilenames=[]
        for i,well in enumerate(self.well_las_attr_dict):
            #     if i==2:
                awell=self.well_las_attr_dict[well]
                awell=removeCorruptlas(awell)
                awell=removeSubsets(awell)
                # print_logs(awell)
                # print('************************************')
                # print(awell.keys())
                if len(awell.keys())>0:
                    suits=suitify(awell)
                    for w in suits:
                        for fn in suits[w]:
                            selectedfilenames.append(fn)
                # print('************************************')
        return selectedfilenames
    def removeUnselected(self,awell):        
        rewell={}
        for l in awell:
            if l in self.retain_files:
                rewell[l]=awell[l]
        return rewell

    def return_selected_items(self):
        print('Clicke...')
        iterator = QTreeWidgetItemIterator(self.tree.tree )
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
        print(self.retain_files)
        print(self.retain_files_ranges)
        self.tree.close()

        for i,well in enumerate(self.well_las_attr_dict):
            try:
                awell=self.well_las_attr_dict[well]
                awell= self.removeUnselected(awell)
                awell=removeCorruptlas(awell)
                # awell=removeSubsets(awell)
                if len(awell.keys())>0:
                    suits=suitify(awell)
                    print(suits)
                    print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
                    ss=SuitSplice(suits,hist_bins=400,n_big_patches=1)  #
                    print('saved ss.....................................')
                    ss.export(self.parent_path+well+'_spliced.las',0.1524)
            except:
                print('Auto splicing failed for this well... ', well)


    # # tree.show()
    # # sys.exit(app.exec_())
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
