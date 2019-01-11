import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

def main(): 
    treeview_dict={
        'MD':{
            'LWD':{
                'a':['good','better','best'],
                'b':['i','am','good']
            },
            'WireLine':{
                'c':['good','better','best']
            }

        },
        'TVD':{
            'LWD':{
                'a1':['good','better','best'],
                'b1':['i','am','good']
            },
            'WireLine':{
                'c1':['good','better','best']
            }

        }
        
    }
    app     = QApplication (sys.argv)
    tree    = QTreeWidget ()
    item    = QTreeWidgetItem()

    tree.headerItem().setText(0, "col1")
    tree.headerItem().setText(1, "col2")
    tree.headerItem().setText(2, "col3")
    tree.headerItem().setText(3, "Notes")

    for ii in range(3):
        parent = QTreeWidgetItem(tree)
        parent.setText(0, "Parent {}".format(ii))
        parent.setFlags(parent.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
        for x in range(4):
            child = QTreeWidgetItem(parent)
            child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
            child.setText(0, "Child {}".format(x))
            child.setCheckState(0, Qt.Unchecked)

            #create the checkbox
            for i in range(1, 5):
                if i < 3:
                    child.setText(i, "")
                    child.setCheckState(i, Qt.Unchecked)
                if i == 3:
                    child.setText(i, "Any Notes?")
                    child.setFlags(child.flags() | Qt.ItemIsEditable)

    tree.show() 
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()