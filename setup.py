# from distutils.core import setup
# import py2exe
import os
# setup(console=['Loggy-v2.2.py'])
os.environ['TCL_LIBRARY'] = r'D:\adiarun\Anaconda3\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'D:\adiarun\Anaconda3\tcl\tk8.6'

# setup([..])
from cx_Freeze import setup, Executable 
  
setup(name = "GeeksforGeeks" , 
      version = "0.1" , 
      description = "" , 
      executables = [Executable("Loggy_v2_2.py")]) 