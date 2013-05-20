import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.

includes = ['en14.txt']
zip_inc = ['en14.txt']

build_exe_options = {"packages": ["os"], "include_files": includes, "zip_includes": zip_inc}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "concentrate",
        version = "0.1",
        description = "Concentrate letterpress engine",
        options = {"build_exe": build_exe_options},
        executables = [Executable("GUI.py", base=base)])