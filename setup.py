# -*- coding: utf-8 -*-
"""
Created on Sun Aug 28 14:23:01 2022

@author: Zed
"""


from cx_Freeze import setup, Executable
import cx_Freeze
  
exe = [cx_Freeze.Executable("openGOALModLauncher.py", base = "Win32GUI")] 
setup(name = "GeeksforGeeks" ,
      version = "0.1" ,
      description = "" ,
      executables = [Executable("openGOALModLauncher.py")])