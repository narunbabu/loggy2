from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
from LasTree import treeWidgetFrmDict,get_txtdict,write_txtdict

import lasio
from loggy_settings import well_folder, lwdVSwirelineFile, mnomonicsfile    
import numpy as np
from helper import *
# from LasTreeimport get_txtdict as getlogdict
# qt_app = QApplication(sys.argv)
# def write_txtdict(file,delimiter=','):
#             with open(file,'w') as f:
#                 lines=f.writelines()
#                 file_dict={}
#                 for l in lines:
#                     [key,val]=l.split('=')
#                     file_dict[key.strip()]=[v.strip() for v in val.split(delimiter)]
#             return file_dict


class Categorize(QMainWindow):

    def __init__(self,parent=None):
        super(Categorize, self).__init__(parent)
        # QMainWindow.__init__(self)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.setWindowTitle('Dynamic Categorizer')
        self.setMinimumWidth(600)
        self.removedmnemonicdict={}        
        # self.logs=logs
       

 
        # Create the QVBoxLayout that lays out the whole form
        self.layout = QHBoxLayout(self.centralWidget)

        self.listlogw=QListWidget()
        self.listlogw.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.catelogsw=QTreeWidget() 
        
        self.loglayout = QVBoxLayout()
        self.loglayout.addWidget(self.listlogw)
        self.catelogslayout = QVBoxLayout()

        

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

    def set_params(self,tree,mnemonicsfile,):
        self.logtree=tree
        # .treeview_dict
        self.mnemonicsfile=mnemonicsfile
        self.base_categories=get_txtdict(self.mnemonicsfile,delimiter=' ')
        # print(self.base_categories)\
        try:
            self.logs=tree.treeview_dict['Log']['NA']
        except:
            self.logs=[' ']
        self.category_dict=tree.treeview_dict
        for bkey in self.base_categories.keys():
            self.removedmnemonicdict[bkey]=[]
            if bkey not in tree.treeview_dict['Log'].keys():
                self.category_dict['Log'][bkey]=[]                
        try:
            del self.category_dict['Log']['NA']
        except:
            print('NA Not present')

        # print(self.category_dict)
        self.catelogsw=  treeWidgetFrmDict(self.catelogsw,self.category_dict)
        self.catelogslayout.addWidget(self.catelogsw)
        self.listlogw.addItems(self.logs)

    def setLog2Category(self):
        # print(self.listlogw.selectedItems())
        # print(self.catelogsw.selectedItems())
        if (len(self.catelogsw.selectedItems())<1) |(len(self.listlogw.selectedItems())<1):
            return
        category=self.catelogsw.selectedItems()[0].text(0)
        log_labels=[llist.text() for llist in self.listlogw.selectedItems()]
        self.category_dict['Log'][category]=log_labels
        self.catelogsw.clear()
        # print(self.category_dict)
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
        # print(self.base_categories)     
        for key in self.category_dict['Log']:
            for log in self.category_dict['Log'][key]:
                if not log in self.base_categories[key]:
                    self.base_categories[key].append(log)
        for key in self.removedmnemonicdict:
            for log in self.removedmnemonicdict[key]:
                if log in self.base_categories[key]:
                    self.base_categories[key].remove(log)
                    self.removedmnemonicdict[key].remove(log)      
        # print(self.base_categories) 
        self.category_dict['Log']['NA']= [self.listlogw.item(i).text() for i in range(self.listlogw.count())]
        write_txtdict(self.mnemonicsfile,self.base_categories,delimiter=' ')
        self.logtree.tree.clear()
        self.logtree.buildTreeWidget()
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
class LogCategorize():
    def __init__(self,mnemonicsfile):
          
        self.mnemonicsfile=mnemonicsfile
        self.base_categories=get_txtdict(self.mnemonicsfile,delimiter=' ')
    def set_las(self,las ):
        self.las=las
    def isResistivityCurve(self,log_cate):
        if(log_cate in ['LLD','LLS','MSFL']):
            return True
        else:
            return False 
    def get_catePresent(self):
        cate_present=[]
        for key in self.treeview_dict:
            if (len(self.treeview_dict[key])>0)&(key!='NA'):
                cate_present.append(key)

        return cate_present
    def get_category(self,log_mnemo,cat_dict):
        #     filewords=multi_split(file_str,delims=['_','-','.'])
            for key in cat_dict:
                if log_mnemo in cat_dict[key]:
                    return key
            return 'NA'
    def getLogsPresent(self):
        logs=[]
        for key in self.treeview_dict:
            if (len(self.treeview_dict[key])>0)&(key!='NA'):
                logs.append(self.treeview_dict[key][0])

        return logs
    def get_lasdepthrange(self):
        # dindx=find_depth_indx(self.las)
        return (self.las.well['STRT']['value'],self.las.well['STOP']['value'])
        # return (self.las[dindx][0],self.las[dindx][-1])
    def get_curverange(self,key):
        dindx=find_depth_indx(self.las)
        data_indxs=~np.isnan(self.las[key])
        return (self.las[dindx][data_indxs][0],self.las[dindx][data_indxs][-1])
    def lasCategorize(self): 
        type_dict=get_txtdict(self.mnemonicsfile,delimiter=' ')
        las_r_log_groups=list(self.las.keys())
        self.treeview_dict={}            
        for k in type_dict.keys(): self.treeview_dict[k]=[] 
        self.treeview_dict['NA']=[]
        for key in las_r_log_groups:
            found=False
            for k in type_dict.keys():                 
                if key in type_dict[k]:
                    self.treeview_dict[k].append(key)
                    found=True
                    break
            if not found:
               self.treeview_dict['NA'].append(key)

def main():
    # treeview_dict={'Log': {'GR': ['GR_ARC'], 'RHOB': ['RHOB', 'ROBB'], 'NPHI': ['TNPH'], 'NA': ['DEPT', 'ROP5_RM', 'A16H', 'A22H', 'A28H', 'A34H', 'A40H', 'P16H', 'P22H', 'P28H', 'P34H', 'P40H', 'A16L', 'A22L', 'A28L', 'A34L', 'A40L', 'P16L', 'P22L', 'P28L', 'P34L', 'P40L', 'ECD_ARC', 'APRS_ARC', 'ATMP', 'DRHO', 'DRHB', 'DCHO', 'DCVE', 'DCAV', 'VERD', 'HORD']}}
    # mnomonicsfile=r'D:\Ameyem Office\Projects\Cairn/mnemonics.txt'

    # app = QApplication(sys.argv)
    # main = Categorize()
    # main.set_params(treeview_dict,mnomonicsfile)
    # main.show()
    # sys.exit(app.exec_())


    files_w_path=well_folder+'W1_SUITE2_COMPOSITE.las'

    las=lasio.read(files_w_path)

    lc=LogCategorize(mnomonicsfile)
    lc.set_las(las)
    lc.lasCategorize()
    print(lc.treeview_dict)
    print(lc.get_catePresent())
    print( lc.get_lasdepthrange())
    print( lc.get_curverange('CAL'))
    lcates=lc.get_catePresent()
    for l in lcates:
        for key in lc.treeview_dict[l]:
            print('{}: {}'.format(key, lc.get_curverange(key)))
if __name__ == '__main__':
    main()