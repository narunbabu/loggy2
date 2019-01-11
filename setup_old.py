import os
import sys
from cx_Freeze import setup, Executable 

# setup(name = "DigImage" , 
#       version = "0.1" , 
#       description = "This software will help to digitize well logs" , 
#       executables = [Executable(script="log_digitize.py",base = "Win32GUI")]) 

os.environ['TCL_LIBRARY'] = r'D:\adiarun\Anaconda3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'D:\adiarun\Anaconda3\tcl\tk8.6'

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "DigImage",
        version = "0.1",
        description = "This software will help to digitize well logs",
        options = {"build_exe": build_exe_options},
        executables = [Executable("Loggy_v2_2.py", base=base)])