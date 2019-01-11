import sys
import os
import json
import glob
from cx_Freeze import setup, Executable
# from GUI.Meta import *

# from PyInstaller import log as logging 
# from PyInstaller import compat
# from os import listdir

# mkldir = compat.base_prefix + "/Lib/site-packages/numpy/core" 
# logger = logging.getLogger(__name__)
# logger.info("MKL installed as part of numpy, importing that!")
# binaries = [(mkldir + "/" + mkl, '') for mkl in listdir(mkldir) if mkl.startswith('mkl_')] 




PythonPath = os.path.split(sys.executable)[0] #get python path

os.environ['TCL_LIBRARY'] = os.path.join(PythonPath,"tcl","tcl8.6")
os.environ['TK_LIBRARY']  = os.path.join(PythonPath,"tcl","tk8.6")

# mkl_files_json_file = glob.glob(os.path.join(PythonPath, "conda-meta","mkl-[!service]*.json"))[0] #json files that has mkl files list (exclude the "service" file)
# with open(mkl_files_json_file) as file:
#     mkl_files_json_data = json.load(file)

# numpy_mkl_dlls = mkl_files_json_data["files"] #get the list of files from the json data file

# np_dlls_fullpath = list(map(lambda currPath: os.path.join(PythonPath,currPath),numpy_mkl_dlls)) #get the full path of these files

# additional_mods = ['numpy.core._methods', 'numpy.lib.format']

# print(np_dlls_fullpath)
# includefiles = np_dlls_fullpath

target = Executable("Loggy.py")

setup(
    name = "My program",
    version = '1.0',
    description = "Program",
    options = {'build_exe': {    'includes': ["sip","re","atexit","PyQt5.QtCore","PyQt5.QtGui","PyQt5.QtWidgets",
    "multiprocessing",'numpy.core._methods', 'numpy.lib.format',
    ]}},
    executables = [target])